"""
Email Service - Handles OTP generation, sending, and verification.
Uses Gmail API (HTTPS REST API) — works on Render since no SMTP ports are needed.
"""
import random
import requests
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db_connection import db
from config.settings import settings
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


OTP_EXPIRY_MINUTES = 10

def generate_otp() -> str:
    """Generate a cryptographically safe 6-digit OTP."""
    return str(random.SystemRandom().randint(100000, 999999))


def get_gmail_service():
    """Builds and returns the Gmail API service using the stored Refresh Token."""
    creds = Credentials(
        token=None,
        refresh_token=settings.GMAIL_REFRESH_TOKEN,
        client_id=settings.GMAIL_CLIENT_ID,
        client_secret=settings.GMAIL_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token"
    )
    return build('gmail', 'v1', credentials=creds, cache_discovery=False)


def test_smtp_connectivity():
    """
    Diagnostic — tests email configuration.
    Returns a dict with results.
    """
    print(f"[EmailService] Using Gmail HTTPS API.")
    print(f"[EmailService] GMAIL_REFRESH_TOKEN set: {bool(settings.GMAIL_REFRESH_TOKEN)}")
    print(f"[EmailService] SMTP_FROM set: {bool(settings.SMTP_FROM)}")
    return {
        "mode": "Gmail HTTP API (not SMTP)",
        "api_key_set": bool(settings.GMAIL_REFRESH_TOKEN),
        "from_email": settings.SMTP_FROM,
        "note": "Render blocks SMTP ports. Gmail API uses HTTPS (port 443)."
    }


def send_otp_email(to_email: str, otp: str, purpose: str = 'verify') -> bool:
    """
    Send an OTP email via Gmail HTTPS API.
    purpose: 'verify' for email verification, 'reset' for password reset.
    Returns True on success, False on failure.
    """
    if not settings.GMAIL_REFRESH_TOKEN or not settings.GMAIL_CLIENT_ID:
        print("[EmailService] ERROR: Gmail API credentials not configured.")
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

    try:
        service = get_gmail_service()
        
        message = EmailMessage()
        message.set_content(html_content, subtype='html')
        message['To'] = to_email
        message['From'] = settings.SMTP_FROM
        message['Subject'] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        service.users().messages().send(userId="me", body=create_message).execute()

        print(f"[EmailService] SUCCESS: OTP email sent to {to_email} via Gmail API (purpose: {purpose})")
        return True

    except HttpError as error:
        print(f"[EmailService] ERROR: Gmail API returned: {error}")
        return False
    except Exception as e:
        print(f"[EmailService] ERROR: Gmail API error: {type(e).__name__}: {e}")
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
