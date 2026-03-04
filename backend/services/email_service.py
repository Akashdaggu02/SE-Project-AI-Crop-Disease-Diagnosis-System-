"""
Email Service - Handles OTP generation, sending, and verification.
Uses EmailJS (HTTPS REST API) — works on Render since no SMTP ports are needed.
Sends through your connected Gmail account via EmailJS.
"""
import random
import requests
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db_connection import db
from config.settings import settings


OTP_EXPIRY_MINUTES = 10

EMAILJS_API_URL = "https://api.emailjs.com/api/v1.0/email/send"


def generate_otp() -> str:
    """Generate a cryptographically safe 6-digit OTP."""
    return str(random.SystemRandom().randint(100000, 999999))


def test_smtp_connectivity():
    """
    Diagnostic — tests email configuration.
    Returns a dict with results.
    """
    print(f"[EmailService] Using EmailJS REST API (not SMTP).")
    print(f"[EmailService] EMAILJS_SERVICE_ID set: {bool(settings.EMAILJS_SERVICE_ID)}")
    print(f"[EmailService] EMAILJS_TEMPLATE_ID set: {bool(settings.EMAILJS_TEMPLATE_ID)}")
    print(f"[EmailService] EMAILJS_PUBLIC_KEY set: {bool(settings.EMAILJS_PUBLIC_KEY)}")
    return {
        "mode": "EmailJS HTTPS API (not SMTP)",
        "service_id": settings.EMAILJS_SERVICE_ID,
        "template_id": settings.EMAILJS_TEMPLATE_ID,
        "public_key_set": bool(settings.EMAILJS_PUBLIC_KEY),
        "note": "Render blocks SMTP ports. EmailJS uses HTTPS (port 443) and sends through Gmail."
    }


def send_otp_email(to_email: str, otp: str, purpose: str = 'verify') -> bool:
    """
    Send an OTP email via EmailJS REST API.
    purpose: 'verify' for email verification, 'reset' for password reset.
    Returns True on success, False on failure.
    """
    service_id = settings.EMAILJS_SERVICE_ID
    template_id = settings.EMAILJS_TEMPLATE_ID
    public_key = settings.EMAILJS_PUBLIC_KEY

    if not service_id or not template_id or not public_key:
        print("[EmailService] ❌ EmailJS credentials not configured. Set EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, EMAILJS_PUBLIC_KEY.")
        return False

    # Build the template parameters that match the EmailJS template variables
    # Template uses: {{email}}, {{passcode}}, {{time}}
    template_params = {
        "email": to_email,
        "passcode": otp,
        "time": f"{OTP_EXPIRY_MINUTES} minutes",
    }

    payload = {
        "service_id": service_id,
        "template_id": template_id,
        "user_id": public_key,
        "template_params": template_params,
    }

    try:
        response = requests.post(
            EMAILJS_API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        if response.status_code == 200:
            print(f"[EmailService] ✅ OTP email sent to {to_email} via EmailJS (purpose: {purpose})")
            return True
        else:
            print(f"[EmailService] ❌ EmailJS returned {response.status_code}: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"[EmailService] ❌ EmailJS request timed out")
        return False
    except Exception as e:
        print(f"[EmailService] ❌ EmailJS error: {type(e).__name__}: {e}")
        return False


def store_otp(email: str, otp: str, purpose: str) -> None:
    """
    Store OTP in MongoDB `otp_tokens` collection.
    Overwrites any previous OTP for the same email + purpose combination.
    """
    try:
        db.db['otp_tokens'].delete_many({'email': email, 'purpose': purpose})
    except Exception:
        pass

    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=OTP_EXPIRY_MINUTES)
    db.execute_insert(
        collection='otp_tokens',
        document={
            'email': email.lower().strip(),
            'otp': otp,
            'purpose': purpose,
            'expires_at': expiry,
            'used': False,
            'created_at': datetime.datetime.utcnow()
        }
    )


def verify_otp(email: str, otp: str, purpose: str) -> dict:
    """
    Verify an OTP for the given email and purpose.
    Returns {'valid': True} or {'valid': False, 'error': 'reason'}.
    """
    results = db.execute_query(
        collection='otp_tokens',
        mongo_query={
            'email': email.lower().strip(),
            'purpose': purpose,
            'used': False
        }
    )

    if not results:
        return {'valid': False, 'error': 'No OTP found. Please request a new one.'}

    token = sorted(results, key=lambda x: x.get('created_at', datetime.datetime.min), reverse=True)[0]

    if datetime.datetime.utcnow() > token.get('expires_at', datetime.datetime.min):
        return {'valid': False, 'error': 'OTP has expired. Please request a new one.'}

    if token.get('otp') != otp.strip():
        return {'valid': False, 'error': 'Invalid OTP. Please try again.'}

    try:
        db.db['otp_tokens'].update_one(
            {'_id': token['_id']},
            {'$set': {'used': True}}
        )
    except Exception:
        pass

    return {'valid': True}
