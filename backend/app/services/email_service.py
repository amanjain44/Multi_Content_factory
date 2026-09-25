import logging
import os
from typing import Optional

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
        
        if env in ("development", "test", "demo"):
            # DEVELOPMENT/DEMO MODE: Output the reset link safely to backend logs
            print("=" * 60)
            print("DEVELOPMENT MODE - PASSWORD RESET LINK GENERATED")
            print(f"Email: {email}")
            print(f"Link:  {reset_link}")
            print("=" * 60)
        else:
            # PRODUCTION MODE: 
            # This is where you would call SendGrid, AWS SES, Resend, etc.
            # Do NOT print the token/link to the logs in production.
            
            # Example placeholder for real integration:
            # if not settings.SMTP_HOST:
            #     raise Exception("Email provider not configured")
            
            logger.info(f"Sending password reset email to {email} (Simulated in Production)")
            # Simulated failure if no provider is actually hooked up, or silently drop.
            pass
