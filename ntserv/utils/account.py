import smtplib
import ssl
from email.message import EmailMessage

from ..libserver import Response
from ..postgres import psql
from ..settings import PROD_EMAIL, PROD_EMAIL_PASS, SERVER_HOST


def user_id_from_username(username):
    pg_result = psql("SELECT id FROM users WHERE username=%s", [username])
    if pg_result.err_msg or not pg_result.rows:
        return None

    return pg_result.row["id"]


def user_id_from_unver_email(email):
    pg_result = psql(
        "SELECT user_id from emails WHERE email=%s AND activated='f'", [email]
    )
    if pg_result.err_msg or not pg_result.rows:
        return None

    return pg_result.row["user_id"]


# ----------------------
# Sending emails
# ----------------------


def email(recipient, subject, body):
    """ Sends an email to ourselves """

    port = 465  # For SSL

    msg = EmailMessage()
    msg["From"] = PROD_EMAIL
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        # Login and send
        server.login(PROD_EMAIL, PROD_EMAIL_PASS)
        server.send_message(msg)


def send_activation_email(recipient, token):
    """ Sends an onboarding email """

    email(
        recipient,
        subject="Activate your Nutra account!",
        body=f"Click the link to activate your account: {SERVER_HOST}/confirm_email?email={recipient}&token={token}",
    )
