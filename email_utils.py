import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(application_user_email, subject, body):
    """
    Sends an email notification to a bus-pass applicant.

    The sender Gmail address and Gmail App Password are read from .env:
        MAIL_USERNAME
        MAIL_PASSWORD

    If email configuration is missing or sending fails, the function
    returns False and the main application continues normally.
    """

    sender_email = os.getenv("MAIL_USERNAME")
    sender_password = os.getenv("MAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("EMAIL WARNING: MAIL_USERNAME or MAIL_PASSWORD is not configured.")
        print("Email notification was skipped.")
        return False

    if not application_user_email:
        print("EMAIL WARNING: Applicant email address is missing.")
        return False

    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = application_user_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(
                sender_email,
                application_user_email,
                message.as_string()
            )

        print(f"EMAIL SENT: {subject} -> {application_user_email}")
        return True

    except Exception as e:
        print(f"EMAIL ERROR: {e}")
        print("The application will continue even though the email was not sent.")
        return False
