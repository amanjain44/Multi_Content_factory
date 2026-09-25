import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_password_reset(email: str, reset_link: str) -> None:
        """
        Sends a password reset email.
        In development/demo mode, it will safely output the link to the logs for manual testing.
        In production, this should integrate with a real email provider.
        """
        env = os.environ.get("ENV", "development").lower()
        
        smtp_host = settings.SMTP_HOST
        smtp_port = settings.SMTP_PORT if settings.SMTP_PORT else 587
        smtp_user = settings.SMTP_USER
        smtp_password = settings.SMTP_PASSWORD
        smtp_from = settings.SMTP_FROM_EMAIL if settings.SMTP_FROM_EMAIL else smtp_user
        
        # If SMTP is configured, send the real email regardless of the environment
        if smtp_host and smtp_user and smtp_password:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = "Reset Your Password - MCF Content Studio"
                msg["From"] = smtp_from
                msg["To"] = email

                text_content = f"You requested a password reset. Click the link below to create a new password:\n\n{reset_link}\n\nIf you did not request this, please ignore this email."
                html_content = f"""
                <html>
                  <body>
                    <h2>Password Reset Request</h2>
                    <p>You recently requested to reset your password for your MCF Content Studio account.</p>
                    <p>Click the link below to securely create a new password:</p>
                    <p><a href="{reset_link}" style="display:inline-block;padding:10px 20px;background-color:#6366f1;color:white;text-decoration:none;border-radius:5px;">Reset Password</a></p>
                    <p>If you didn't make this request, you can safely ignore this email.</p>
                  </body>
                </html>
                """
                
                part1 = MIMEText(text_content, "plain")
                part2 = MIMEText(html_content, "html")
                msg.attach(part1)
                msg.attach(part2)

                print(f"Attempting to connect to {smtp_host}:{smtp_port}...")
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_from, email, msg.as_string())
                server.quit()
                
                print(f"✅ Real password reset email successfully sent to {email}")
                return
            except Exception as e:
                print(f"❌ Failed to send real email via SMTP: {str(e)}")
                # Fall back to logging if email fails to send in dev mode
                if env not in ("development", "test", "demo"):
                    raise e
        
        # Fallback for local development when SMTP is not configured
        if env in ("development", "test", "demo"):
            print("=" * 60)
            print("DEVELOPMENT MODE - SMTP NOT CONFIGURED")
            print("To send real emails, add SMTP_HOST, SMTP_USER, and SMTP_PASSWORD to your .env file.")
            print(f"Email: {email}")
            print(f"Link:  {reset_link}")
            print("=" * 60)
        else:
            print(f"⚠️ WARNING: Trying to send password reset to {email} in PRODUCTION but SMTP variables are missing in .env!")
