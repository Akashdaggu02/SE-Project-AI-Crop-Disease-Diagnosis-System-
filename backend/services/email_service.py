"""
Email Service - Handles OTP generation, sending, and verification.
Uses SendGrid (HTTPS REST API) — works on Render since no SMTP ports are needed.
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

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


def generate_otp() -> str:
    """Generate a cryptographically safe 6-digit OTP."""
    return str(random.SystemRandom().randint(100000, 999999))


def test_smtp_connectivity():
    """
    Diagnostic — tests email configuration.
    Returns a dict with results.
    """
    print(f"[EmailService] Using SendGrid REST API (not SMTP).")
    print(f"[EmailService] SENDGRID_API_KEY set: {bool(settings.SENDGRID_API_KEY)}")
    print(f"[EmailService] SENDGRID_FROM_EMAIL set: {bool(settings.SENDGRID_FROM_EMAIL)}")
    return {
        "mode": "SendGrid HTTPS API (not SMTP)",
        "api_key_set": bool(settings.SENDGRID_API_KEY),
        "from_email": settings.SENDGRID_FROM_EMAIL,
        "note": "Render blocks SMTP ports. SendGrid uses HTTPS (port 443)."
    }


def send_otp_email(to_email: str, otp: str, purpose: str = 'verify') -> bool:
    """
    Send an OTP email via SendGrid REST API.
    purpose: 'verify' for email verification, 'reset' for password reset.
    Returns True on success, False on failure.
    """
    api_key = settings.SENDGRID_API_KEY
    from_email = settings.SENDGRID_FROM_EMAIL

    if not api_key or not from_email:
        print("[EmailService] ERROR: SendGrid credentials not configured.")
        return False

    subject = "Verify Your Email - AI Crop Diagnosis"
    if purpose == 'reset':
        subject = "Password Reset OTP - AI Crop Diagnosis"

    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
        <h2>AI Crop Diagnosis</h2>
        <p>Hello,</p>
        <p>Your one-time password (OTP) is: <strong style="font-size: 24px;">{otp}</strong></p>
        <p>This code will expire in {OTP_EXPIRY_MINUTES} minutes.</p>
        <p>If you did not request this OTP, please ignore this email.</p>
    </div>
    """

    payload = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": subject
            }
        ],
        "from": {
            "email": from_email,
            "name": "AI Crop Diagnosis"
        },
        "content": [
            {
                "type": "text/html",
                "value": html_content
            }
        ]
    }

    try:
        response = requests.post(
            SENDGRID_API_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=15
        )

        if response.status_code in (200, 202):
            print(f"[EmailService] SUCCESS: OTP email sent to {to_email} via SendGrid (purpose: {purpose})")
            return True
        else:
            print(f"[EmailService] ERROR: SendGrid returned {response.status_code}: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"[EmailService] ERROR: SendGrid request timed out")
        return False
    except Exception as e:
        print(f"[EmailService] ERROR: SendGrid error: {type(e).__name__}: {e}")
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
