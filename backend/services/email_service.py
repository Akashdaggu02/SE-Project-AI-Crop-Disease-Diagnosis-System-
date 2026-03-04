"""
Email Service - Handles OTP generation, sending, and verification.
Uses Resend (HTTPS API) instead of SMTP — required because Render blocks all SMTP ports.
Sign up for free at https://resend.com — 3,000 emails/month free.
"""
import random
import resend
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db_connection import db
from config.settings import settings


OTP_EXPIRY_MINUTES = 10


def generate_otp() -> str:
    """Generate a cryptographically safe 6-digit OTP."""
    return str(random.SystemRandom().randint(100000, 999999))


def _get_resend_client():
    """Configure and return the Resend API key."""
    api_key = settings.RESEND_API_KEY
    if not api_key:
        raise ValueError("[EmailService] ❌ RESEND_API_KEY is not set. Get a free key at https://resend.com")
    resend.api_key = api_key


def test_smtp_connectivity():
    """
    Diagnostic — tests email configuration.
    Returns a dict with results.
    """
    print(f"[EmailService] SMTP is not used — Render blocks SMTP ports.")
    print(f"[EmailService] Using Resend API instead.")
    print(f"[EmailService] RESEND_API_KEY set: {bool(settings.RESEND_API_KEY)}")
    print(f"[EmailService] SMTP_FROM (sender): {settings.SMTP_FROM}")
    return {
        "mode": "Resend HTTP API (not SMTP)",
        "RESEND_API_KEY_set": bool(settings.RESEND_API_KEY),
        "sender": settings.SMTP_FROM,
        "note": "Render blocks SMTP ports 465 and 587. Resend uses HTTPS (port 443)."
    }


def send_otp_email(to_email: str, otp: str, purpose: str = 'verify') -> bool:
    """
    Send an OTP email via Resend API.
    purpose: 'verify' for email verification, 'reset' for password reset.
    Returns True on success, False on failure.
    """
    try:
        _get_resend_client()
    except ValueError as e:
        print(str(e))
        return False

    if purpose == 'reset':
        subject = "🔑 Password Reset OTP - Agri-AI"
        body_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto; background: #f9f9f9; border-radius: 12px; overflow: hidden;">
          <div style="background: linear-gradient(135deg, #2e7d32, #4caf50); padding: 32px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 26px;">🌾 Agri-AI</h1>
            <p style="color: #c8e6c9; margin: 8px 0 0 0;">AI Crop Diagnosis System</p>
          </div>
          <div style="padding: 32px; background: white;">
            <h2 style="color: #2e7d32; margin-top: 0;">Password Reset Request</h2>
            <p style="color: #555; line-height: 1.6;">We received a request to reset your password. Use the OTP below to create a new password.</p>
            <div style="background: #e8f5e9; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0;">
              <p style="color: #555; margin: 0 0 8px 0; font-size: 14px;">Your One-Time Password</p>
              <span style="font-size: 40px; font-weight: bold; color: #2e7d32; letter-spacing: 10px;">{otp}</span>
            </div>
            <p style="color: #888; font-size: 13px;">⏰ This OTP is valid for <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.</p>
            <p style="color: #888; font-size: 13px;">If you did not request this, please ignore this email. Your password will remain unchanged.</p>
          </div>
          <div style="padding: 16px; background: #f0faf0; text-align: center;">
            <p style="color: #aaa; font-size: 12px; margin: 0;">© 2026 Agri-AI — AI Crop Diagnosis System</p>
          </div>
        </div>
        """
    else:
        subject = "✅ Email Verification OTP - Agri-AI"
        body_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto; background: #f9f9f9; border-radius: 12px; overflow: hidden;">
          <div style="background: linear-gradient(135deg, #2e7d32, #4caf50); padding: 32px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 26px;">🌾 Agri-AI</h1>
            <p style="color: #c8e6c9; margin: 8px 0 0 0;">AI Crop Diagnosis System</p>
          </div>
          <div style="padding: 32px; background: white;">
            <h2 style="color: #2e7d32; margin-top: 0;">Verify Your Email</h2>
            <p style="color: #555; line-height: 1.6;">Welcome to Agri-AI! Please verify your email address to activate your account.</p>
            <div style="background: #e8f5e9; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0;">
              <p style="color: #555; margin: 0 0 8px 0; font-size: 14px;">Your Verification Code</p>
              <span style="font-size: 40px; font-weight: bold; color: #2e7d32; letter-spacing: 10px;">{otp}</span>
            </div>
            <p style="color: #888; font-size: 13px;">⏰ This code is valid for <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.</p>
            <p style="color: #888; font-size: 13px;">If you did not create an Agri-AI account, please ignore this email.</p>
          </div>
          <div style="padding: 16px; background: #f0faf0; text-align: center;">
            <p style="color: #aaa; font-size: 12px; margin: 0;">© 2026 Agri-AI — AI Crop Diagnosis System</p>
          </div>
        </div>
        """

    try:
        params: resend.Emails.SendParams = {
            "from": f"Agri-AI <{settings.SMTP_FROM}>",
            "to": [to_email],
            "subject": subject,
            "html": body_html,
        }
        response = resend.Emails.send(params)
        email_id = response.get("id") if isinstance(response, dict) else getattr(response, "id", None)
        print(f"[EmailService] ✅ OTP email sent to {to_email} via Resend (purpose: {purpose}, id: {email_id})")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"[EmailService] SMTP Authentication failed - check SMTP_USER and SMTP_PASS: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"[EmailService] SMTP error: {e}")
        return False
    except Exception as e:
        print(f"[EmailService] ❌ Resend error: {type(e).__name__}: {e}")
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
