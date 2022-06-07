import re
import uuid

import bcrypt

from ntserv.libserver import (
    BadRequest400Response,
    MultiStatus207Response,
    NotImplemented501Response,
    Success200Response,
    Unauthenticated401Response,
    slack_msg,
)
from ntserv.postgres import psql
from ntserv.utils.account import (
    cmp_pass,
    send_activation_email,
    user_id_from_unver_email,
    user_id_from_username_or_email,
)
from ntserv.utils.auth import (
    AUTH_LEVEL_UNCONFIRMED,
    auth,
    issue_jwt_token,
)


def POST_register(request):
    # Parse incoming request
    body = request.json
    email = body["email"]
    slack_msg(f"USER REGISTER: {email}")

    username = body.get("username")
    password = body.get("password")
    password_confirm = body.get("password-confirm")

    # TODO: break up below block into "service-level" function

    # -------------------------------------
    # Registration validation checks
    # -------------------------------------

    ##################
    # Email (required)

    regex = (
        r"""^(([^<>()\[\]\\.,:\s@"]+(\.[^<>()\[\]\\.,:\s@"]+)*)|(".+"))@((\[["""
        r"""0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+["""
        r"""a-zA-Z]{2,}))$"""
    )
    if not re.match(regex, email):
        return BadRequest400Response("Email address not recognizable")
    # Allow "guest" registration with email only
    # Email exists already?
    pg_result = psql("SELECT user_id FROM emails WHERE email=%s", [email])
    if pg_result.rows:
        return MultiStatus207Response(data={"user_id": pg_result.row["user_id"]})
    ##########
    # Username
    elif username and (
        len(username) < 6
        or len(username) > 18
        or not re.match("^[0-9a-z_]+$", username)
    ):
        return BadRequest400Response(
            "Username must be 6-18 chars, and contain "
            "only lowercase letters, numbers, and underscores"
        )
    ##########
    # Password
    elif password and password_confirm != password:
        return BadRequest400Response("Passwords do NOT match")
    elif password and (
        len(password) < 6
        or len(password) > 40
        or not re.findall(r"""[~`!#$%\^&*+=\-\[\]\\',/{}|\\":<>\?]""", password)
        or not re.findall("[a-z]", password)
        or not re.findall("[A-Z]", password)
    ):
        return BadRequest400Response(
            "Password must be 6-40 chars long, and contain "
            "an uppercase, a lowercase, and a special character"
        )

    # -------------------------------------
    # Attempt to SQL insert user
    # -------------------------------------
    # TODO: transactional `block()`
    # CREATE USER
    if password:
        passwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    else:
        passwd = None
    pg_result = psql(
        "INSERT INTO users (username, passwd) VALUES (%s, %s) RETURNING id",
        [username, passwd],
    )
    # ERRORs
    if pg_result.err_msg:
        return pg_result.Response
    user_id = pg_result.row["id"]
    # Insert emails
    pg_result = psql(
        "INSERT INTO emails (user_id, email, main) VALUES (%s, %s, %s) RETURNING email",
        [user_id, email, True],
    )
    # ERRORs
    if pg_result.err_msg:
        psql("DELETE FROM users WHERE id=%s RETURNING id", [user_id])
        return pg_result.Response
    # Insert tokens
    token = str(uuid.uuid4()).replace("-", "")
    pg_result = psql(
        "INSERT INTO tokens (user_id, token, type) VALUES (%s, %s, %s) RETURNING token",
        [user_id, token, "EMAIL_TOKEN_ACTIVATE"],
    )
    # ERRORs
    if pg_result.err_msg:
        psql("DELETE FROM emails WHERE user_id=%s RETURNING email", [user_id])
        psql("DELETE FROM users WHERE id=%s RETURNING id", [user_id])
        return pg_result.Response
    #
    # Send activation email
    send_activation_email(email, token)

    # TODO: rethink "message"?
    return Success200Response("Successfully registered", data={"id": user_id})


def POST_login(request):
    # Parse incoming request
    username = request.json["username"]
    password = request.json["password"]
    slack_msg(f"USER LOGIN: {username}")

    # See if user exists
    user_id = user_id_from_username_or_email(username)
    if not user_id:
        return BadRequest400Response(f"No user found: {username}")

    # Get auth level and return JWT (token)
    token, auth_level, error = issue_jwt_token(user_id, password)
    if token:
        return Success200Response(
            "Logged in", {"token": token, "auth-level": auth_level}
        )
    else:
        return BadRequest400Response(error)


def POST_v2_login(request):
    email = request.json["email"]
    password = request.json["password"]

    user_agent = request.user_agent.string
    oper_sys = request.json["os"]
    username = request.json.get("username")
    hostname = request.json.get("hostname")

    device_id = f"{oper_sys} {username}@{hostname} {user_agent}"

    #
    # See if user exists
    user_id = user_id_from_username_or_email(email)
    if not user_id:
        return BadRequest400Response(f"No user found: {email}")

    #
    # Get auth level and return JWT (token)
    token, auth_level, error = issue_oauth_token(user_id, password, device_id)
    if token:
        return Success200Response(
            "Logged in", data={"token": token, "auth-level": auth_level}
        )
    else:
        BadRequest400Response(error)


@auth
def GET_user_details(request, level=AUTH_LEVEL_UNCONFIRMED, user_id=None):
    # TODO: if not user_id: return err
    pg_result = psql("SELECT * FROM users(%s)", [user_id])
    return Success200Response(data=pg_result.row)


def GET_confirm_email(request):
    # TODO: redirect code with user-friendly, non-JSON output

    email = request.args["email"]
    token = request.args["token"]
    slack_msg(f"USER ACTIVATE: {email}")

    user_id = user_id_from_unver_email(email)
    if not user_id:
        return BadRequest400Response("No such user")

    # Grab token(s)
    pg_result = psql(
        "SELECT token FROM tokens WHERE user_id=%s AND type='EMAIL_TOKEN_ACTIVATE'",
        [user_id],
    )
    if pg_result.err_msg or not pg_result.rows:
        return BadRequest400Response("No token for you")
    # Compare token(s)
    valid = any(r["token"] == token for r in pg_result.rows)
    if not valid:
        return Unauthenticated401Response("Wrong token")
    # ---------------------
    # Update info
    # ---------------------
    # TODO: transactional `block()`
    pg_result = psql(
        """
UPDATE
  emails
SET
  activated = 't'
WHERE
  user_id = %s
  AND activated = 'f'
RETURNING
  user_id
        """,
        [user_id],
    )
    pg_result = psql(
        """
DELETE FROM tokens
WHERE user_id = %s
  AND TYPE = 'EMAIL_TOKEN_ACTIVATE'
RETURNING
  user_id
        """,
        [user_id],
    )
    # TODO: send welcome email?
    return Success200Response("Successfully activated")


@auth
def GET_email_change(request, level=AUTH_LEVEL_UNCONFIRMED, user_id=None):
    email = request.args["email"]
    password = request.args["password"]

    # Require additional password check
    if not cmp_pass(user_id, password):
        return Unauthenticated401Response("Invalid password")

    # TODO: implement
    return NotImplemented501Response(data={"email": email})


@auth
def GET_password_change(request, level=AUTH_LEVEL_UNCONFIRMED, user_id=None):
    password_old = request.args["password_old"]
    password = request.args["password"]
    password_confirm = request.args["password_confirm"]

    # Require additional password check
    if not cmp_pass(user_id, password_old):
        return Unauthenticated401Response("Invalid password")
    # Check matching passwords
    if password != password_confirm:
        return BadRequest400Response("Passwords don't match")

    # Update
    passwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    psql(
        "UPDATE users SET passwd=%s WHERE user_id=%s RETURNING user_id",
        [passwd, user_id],
    )

    # TODO: return a message?
    return Success200Response()


def POST_username_forgot(request):
    return NotImplemented501Response()


def POST_password_new_request(request):
    return NotImplemented501Response()


def POST_password_new_reset(request):
    return NotImplemented501Response()


# ---------------
# File a report
# ---------------
@auth
def POST_report(request, level=AUTH_LEVEL_UNCONFIRMED, user_id=None):
    report_type = request.json["report_type"]
    report_message = request.json["report_message"]

    psql(
        """
INSERT INTO reports (user_id, report_type, report_message)
  VALUES (%s, %s, %s)
RETURNING
  user_id
        """,
        [user_id, report_type, report_message],
    )

    return Success200Response()
