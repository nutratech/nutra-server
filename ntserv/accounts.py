import re
import uuid

import bcrypt

from .libserver import Response
from .postgres import psql
from .utils.account import (
    cmp_pass,
    send_activation_email,
    user_id_from_unver_email,
    user_id_from_username,
)
from .utils.auth import (
    AUTH_LEVEL_BASIC,
    AUTH_LEVEL_READ_ONLY,
    AUTH_LEVEL_UNCONFIRMED,
    auth,
    issue_token,
    jwt_token,
)


def POST_register(request):

    # Parse incoming request
    body = request.json
    email = body["email"]

    username = body.get("username")
    password = body.get("password")
    password_confirm = body.get("password-confirm")

    # TODO: break up below block into "service-level" function

    # -------------------------------------
    # Registration validation checks
    # -------------------------------------

    ##################
    # Email (required)
    if not re.match(
        r"""^(([^<>()\[\]\\.,:\s@"]+(\.[^<>()\[\]\\.,:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$""",
        email,
    ):
        return Response(data={"error": "Email address not recognizable"}, code=400)
    # Allow "guest" registration with email only
    # Email exists already?
    pg_result = psql("SELECT user_id FROM emails WHERE email=%s", [email])
    if pg_result.rows:
        return Response(data={"user_id": pg_result.row["user_id"]}, code=207)
    ##########
    # Username
    elif username and (
        len(username) < 6
        or len(username) > 18
        or not re.match("^[0-9a-z_]+$", username)
    ):
        return Response(
            data={
                "error": "Username must be 6-18 chars, and contain only lowercase letters, numbers, and underscores"
            },
            code=400,
        )
    ##########
    # Password
    elif password and password_confirm != password:
        return Response(data={"error": "Passwords do NOT match"}, code=400)
    elif password and (
        len(password) < 6
        or len(password) > 40
        or not re.findall(r"""[~`!#$%\^&*+=\-\[\]\\',/{}|\\":<>\?]""", password)
        or not re.findall("[a-z]", password)
        or not re.findall("[A-Z]", password)
    ):
        return Response(
            data={
                "error": "Password must be 6-40 chars long, and contain an uppercase, a lowercase, and a special character",
            },
            code=400,
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
        "INSERT INTO emails (user_id, email) VALUES (%s, %s) RETURNING email",
        [user_id, email],
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

    return Response(data={"message": "Successfully registered", "id": user_id})


def POST_login(request):

    # Parse incoming request
    username = request.json["username"]
    password = request.json["password"]

    #
    # See if user exists
    user_id = user_id_from_username(username)
    if not user_id:
        return Response(
            data={
                "token": None,
                "auth-level": AUTH_LEVEL_READ_ONLY,
                "error": f"No user found: {username}",
            },
            code=202,
        )

    #
    # Get auth level and return JWT (token)
    token, auth_level, error = issue_token(user_id, password)
    if token:
        return Response(data={"token": token, "auth-level": auth_level})
    else:
        return Response(
            data={"token": None, "auth-level": auth_level, "error": error}, code=202
        )


@auth
def GET_user_details(request, level=AUTH_LEVEL_UNCONFIRMED, user_id=None):
    # TODO: if not user_id: return err
    pg_result = psql("SELECT * FROM users(%s)", [user_id])
    return Response(data=pg_result.row)


def GET_confirm_email(request):

    # TODO: redirect code with user-friendly, non-JSON output

    email = request.args["email"]
    token = request.args["token"]

    user_id = user_id_from_unver_email(email)
    if not user_id:
        return Response(data={"error": "No such user"}, code=400)

    # Grab token(s)
    pg_result = psql(
        "SELECT token FROM tokens WHERE user_id=%s AND type='EMAIL_TOKEN_ACTIVATE'",
        [user_id],
    )
    if pg_result.err_msg or not pg_result.rows:
        return Response(data={"error": "No token for you"}, code=400)
    # Compare token(s)
    valid = any(r["token"] == token for r in pg_result.rows)
    if not valid:
        return Response(data={"error": "Wrong"}, code=401)
    # ---------------------
    # Update info
    # ---------------------
    # TODO: transactional `block()`
    pg_result = psql(
        "UPDATE emails SET activated='t' WHERE user_id=%s AND activated='f' RETURNING user_id",
        [user_id],
    )
    pg_result = psql(
        "DELETE FROM tokens WHERE user_id=%s AND type='EMAIL_TOKEN_ACTIVATE' RETURNING user_id",
        [user_id],
    )
    # TODO: send welcome email?
    return Response(data={"message": "Successfully activated"})


@auth
def GET_email_change(request, level=AUTH_LEVEL_UNCONFIRMED, user_id=None):
    email = request.args["email"]
    password = request.args["password"]

    # Require additional password check
    if not cmp_pass(user_id, password):
        return Response(data={"error": "Invalid password"}, code=401)

    # TODO: implement
    return Response(data={"email": email}, code=501)


@auth
def GET_password_change(request, level=AUTH_LEVEL_UNCONFIRMED, user_id=None):

    password_old = request.args["password_old"]
    password = request.args["password"]
    password_confirm = request.args["password_confirm"]

    # Require additional password check
    if not cmp_pass(user_id, password_old):
        return Response(data={"error": "Invalid password"}, code=401)
    # Check matching passwords
    if password != password_confirm:
        return Response(data={"error": "Passwords don't match"}, code=400)

    # Update
    passwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    psql(
        "UPDATE users SET passwd=%s WHERE user_id=%s RETURNING user_id",
        [passwd, user_id],
    )

    # TODO: return a message?
    return Response()


def POST_username_forgot(request):
    return Response(code=501)


def POST_password_new_request(request):
    return Response(code=501)


def POST_password_new_reset(request):
    return Response(code=501)


# ---------------
# File a report
# ---------------
@auth
def POST_report(request, level=AUTH_LEVEL_UNCONFIRMED, user_id=None):
    report_type = request.json["report_type"]
    report_message = request.json["report_message"]

    psql(
        "INSERT INTO reports (user_id, report_type, report_message) VALUES (%s, %s, %s) RETURNING user_id",
        [user_id, report_type, report_message],
    )

    return Response()
