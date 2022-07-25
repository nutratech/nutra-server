"""
Mostly SQL / authorization checking functions.
Also contains the email sending methods, for on-boarding, reset/change password
What's the difference between this and auth.py? It's not totally clear yet!
"""
import smtplib
import ssl
from email.message import EmailMessage

import bcrypt

from ntserv.env import PROD_EMAIL, PROD_EMAIL_PASS, SERVER_HOST
from ntserv.persistence.psql import psql

# TODO: @psql(query="", return='id')
#       @psql(query="", return='all')
#  annotation to support reducing "those three lines" down to 1 annotation


# ----------------------
# get user_id funcs
# ----------------------
def user_id_from_username_or_email(identifier: str) -> int:
    """Get user ID from username OR email"""
    pg_result = psql("SELECT * FROM find_user(%s)", [identifier])
    if pg_result.err_msg or not pg_result.rows:
        # TODO: magic number
        return -65536

    return int(pg_result.row["id"])


def user_id_from_username(username: str) -> int:
    """Get user ID from username"""
    pg_result = psql('SELECT id FROM "user" WHERE username=%s', [username])
    if pg_result.err_msg or not pg_result.rows:
        # TODO: magic number
        return -65536

    return int(pg_result.row["id"])


def user_id_from_unver_email(_email: str) -> int:
    """Get user ID from unverified email"""
    pg_result = psql(
        "SELECT user_id from email WHERE email=%s AND activated='f'", [_email]
    )
    if pg_result.err_msg or not pg_result.rows:
        # TODO: magic number
        return -65536

    return int(pg_result.row["user_id"])


# ----------------------
# password comparator
# ----------------------
def cmp_pass(user_id: int, password: str) -> bool:
    """Compare password with salted hash, see if valid"""
    pg_result = psql('SELECT passwd FROM "user" WHERE id=%s', [user_id])
    passwd = pg_result.row["passwd"]
    return bcrypt.checkpw(password.encode(), passwd.encode())


# ----------------------
# Sending emails
# ----------------------
def email(recipient: str, subject: str, body: str) -> None:
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
        # with smtplib.SMTP_SSL(
        #     "gameguru.heliohost.org", port, context=context
        # ) as server:

        # Login and send
        server.login(PROD_EMAIL, PROD_EMAIL_PASS)
        # server.login("_mainaccount@gameguru.heliohost.org", PROD_EMAIL_PASS)
        # server.login("nutra@gameguru.heliohost.org", PROD_EMAIL_PASS)
        server.send_message(msg)


def send_activation_email(recipient: str, token: str) -> None:
    """Sends an on-boarding email"""

    email(
        recipient,
        subject="Activate your Nutra account!",
        body="Click the link to activate your account: "
        f"{SERVER_HOST}/email/confirm?email={recipient}&token={token}",
    )
