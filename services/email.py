import os
from email.message import EmailMessage

import aiosmtplib
from dotenv import load_dotenv


# Load email settings from the .env file
load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))

SMTP_USERNAME = os.getenv("SMTP_USERNAME") or None
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") or None

SENDER_EMAIL = "no-reply@company-doc-ai.local"


# Send an email through the configured SMTP server
async def send_email(
    recipient: str,
    subject: str,
    body: str
) -> None:

    # Create the email message
    message = EmailMessage()

    message["From"] = SENDER_EMAIL
    message["To"] = recipient
    message["Subject"] = subject

    message.set_content(body)

    # Connect to SMTP and send the email
    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
        start_tls=False,
        use_tls=False,
    )
    