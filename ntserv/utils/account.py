import smtplib
import ssl
from email.message import EmailMessage

import bcrypt

from ntserv.postgres import psql
from ntserv.settings import PROD_EMAIL, PROD_EMAIL_PASS, SERVER_HOST


# ----------------------
# get user_id funcs
# ----------------------
def user_id_from_username_or_email(identifier):
    pg_result = psql("SELECT * FROM find_user(%s)", [identifier])
    if pg_result.err_msg or not pg_result.rows:
        return None

    return pg_result.row["id"]


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
# password comparator
# ----------------------
def cmp_pass(user_id, password):
    pg_result = psql("SELECT passwd FROM users WHERE user_id=%s", [user_id])
    passwd = pg_result.row["passwd"]
    return bcrypt.checkpw(password.encode(), passwd.encode())


# ----------------------
# Sending emails
# ----------------------
def email(recipient, subject, body):
    """Sends an email to ourselves"""

    port = 465  # For SSL
    # port_g = 587 # For Gmail

    msg = EmailMessage()
    msg["From"] = PROD_EMAIL
    msg["To"] = recipient
    msg["Cc"] = PROD_EMAIL  # Send a copy to ourselves
    msg["Subject"] = subject
    msg.set_content(body)

    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        # with smtplib.SMTP_SSL("gameguru.heliohost.org", port, context=context) as server:
        # Login and send
        server.login(PROD_EMAIL, PROD_EMAIL_PASS)
        # server.login("_mainaccount@gameguru.heliohost.org", PROD_EMAIL_PASS)
        # server.login("nutra@gameguru.heliohost.org", PROD_EMAIL_PASS)
        server.send_message(msg)


def send_activation_email(recipient, token):
    """Sends an on-boarding email"""

    email(
        recipient,
        subject="Activate your Nutra account!",
        body="Click the link to activate your account: "
        f"{SERVER_HOST}/email/confirm?email={recipient}&token={token}",
    )
