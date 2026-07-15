import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


def send_contact_email(name: str, email: str, message: str) -> bool:
    """
    Sends an email notification when someone submits the contact form.
    Returns True if sent successfully, False otherwise.
    """

    if not settings.SMTP_EMAIL or not settings.SMTP_PASSWORD:
        # Email not configured — skip silently
        return False

    try:

        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_EMAIL
        msg["To"] = settings.RECEIVER_EMAIL
        msg["Subject"] = f"New Contact Message from {name}"

        body = (
            f"You received a new message from your website contact form.\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n\n"
            f"Message:\n{message}"
        )

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:

            server.starttls()
            server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
            server.send_message(msg)

        return True

    except Exception as e:

        print(f"Email sending failed: {e}")
        return False