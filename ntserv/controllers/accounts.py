import re
import uuid
from typing import Tuple, Union

import bcrypt
import sanic

from ntserv.persistence.psql import psql
from ntserv.utils.account import (
    cmp_pass,
    send_activation_email,
    user_id_from_unver_email,
    user_id_from_username_or_email,
)
from ntserv.utils.auth import (
    AUTH_LEVEL_UNAUTHED,
    AUTH_LEVEL_UNCONFIRMED,
    auth,
    issue_jwt_token,
)
from ntserv.utils.libserver import (
    BadRequest400Response,
    MultiStatus207Response,
    NotImplemented501Response,
    Success200Response,
    Unauthenticated401Response,
)


def post_register(request: sanic.Request) -> sanic.HTTPResponse:
    # Parse incoming request
    body: dict = request.json
    email: str = body["email"]
    # TODO: notify ourselves, via email, of USER REGISTER? This used to be slack_msg()

    username: str = body.get("username", str())
    password: str = body.get("password", str())
    password_confirm: str = body.get("password-confirm", str())

    # TODO: break up below block into "service-level" function

    # -------------------------------------
    # Registration validation checks
    # -------------------------------------

    ##################
    # Email (required)

    regex = (
        r"""^(([^<>()\[\]\\.,:\s@"]+(\.[^<>()\[\]\\.,:\s@"]+)*)|(".+"))@"""
        r"""((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|"""
        r"""(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"""
    )
    if not re.match(regex, email):
        return BadRequest400Response("Email address not recognizable")
    # Allow "guest" registration with email only
    # Email exists already?
    pg_result = psql("SELECT user_id FROM email WHERE email=%s", [email])
    if pg_result.rows:
        return MultiStatus207Response(data={"user_id": pg_result.row["user_id"]})
    ##########
    # Username
    if username and (
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
    if password and password_confirm != password:
        return BadRequest400Response("Passwords do NOT match")
    if password and (
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
        'INSERT INTO "user" (username, passwd) VALUES (%s, %s) RETURNING id',
        [username, passwd],
    )
    # ERRORS
    if pg_result.err_msg:
        return pg_result.http_response_error
    user_id = pg_result.row["id"]
    # Insert emails
    pg_result = psql(
        "INSERT INTO email (user_id, email, main) VALUES (%s, %s, %s) RETURNING email",
        [user_id, email, True],
    )
    # ERRORs
    if pg_result.err_msg:
        psql('DELETE FROM "user" WHERE id=%s RETURNING id', [user_id])
        return pg_result.http_response_error
    # Insert tokens
    token = str(uuid.uuid4()).replace("-", "")
    pg_result = psql(
        "INSERT INTO token (user_id, token, type) VALUES (%s, %s, %s) RETURNING token",
        [user_id, token, "EMAIL_TOKEN_ACTIVATE"],
    )
    # ERRORs
    if pg_result.err_msg:
        psql("DELETE FROM email WHERE user_id=%s RETURNING email", [user_id])
        psql('DELETE FROM "user" WHERE id=%s RETURNING id', [user_id])
        return pg_result.http_response_error
    #
    # Send activation email
    send_activation_email(email, token)

    # TODO: rethink "message"?
    return Success200Response(
        data={"message": "Successfully registered", "id": user_id}
    )


def post_login(request: sanic.Request) -> sanic.HTTPResponse:
    # Parse incoming request
    username = request.json["username"]
    password = request.json["password"]
    # TODO: notify ourselves, via email, of USER LOGIN? This used to be slack_msg()

    # See if user exists
    user_id = user_id_from_username_or_email(username)
    if not user_id:
        return BadRequest400Response(f"No user found: {username}")

    # Get auth level and return JWT (token)
    token, auth_level, error = issue_jwt_token(user_id, password)
    if token:
        return Success200Response(
            data={"message": "Logged in", "token": token, "auth-level": auth_level}
        )
    return BadRequest400Response(error)


def post_v2_login(request: sanic.Request) -> sanic.HTTPResponse:
    def issue_oauth_token(
        *args: Union[str, int],
    ) -> Tuple[int, int, str]:
        """

        @param args: _user_id: int, _passwd: str, _device_id: str
        @return: user_id: int, auth_level: int, token: str
        """
        # TODO: complete this in another module

        # _user_id, _passwd, _device_id
        _ = int(args[0])
        _ = str(args[1])
        _ = str(args[2])

        return -65536, AUTH_LEVEL_UNAUTHED, str()

    username = str(request.json.get("username", str()))
    email = str(request.json.get("email", str()))
    password = str(request.json["password"])

    user_agent = str(request.headers["user-agent"])
    # FIXME: Are these proper? Do we need an app_type too (e.g. web, cli, android)?
    oper_sys = str(request.json["os"])
    hostname = str(request.json["hostname"])

    device_id = f"{oper_sys}-{username}@{hostname}-{user_agent}"

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
            data={"message": "Logged in", "token": token, "auth-level": auth_level}
        )
    return BadRequest400Response(error)


# TODO: resolve unused keywords with **kwargs ?
@auth
def get_user_details(
    request: sanic.Request, level: int = AUTH_LEVEL_UNCONFIRMED, user_id: int = -65536
) -> sanic.HTTPResponse:
    # TODO: if not user_id: return err
    # NOTE: i'm working here... postman jwt error, unused arguments, lots of things
    # NOTE: this IS valid syntax, it DOES work. Pycharm is wrong to complain I guess
    pg_result = psql('SELECT * FROM "user"(%s)', [user_id])
    return Success200Response(data=pg_result.row)


def get_confirm_email(request: sanic.Request) -> sanic.HTTPResponse:
    # TODO: redirect code with user-friendly, non-JSON output

    email = request.args["email"]
    token = request.args["token"]
    # TODO: notify ourselves, via email, of USER ACTIVATE? This used to be slack_msg()

    user_id = user_id_from_unver_email(email)
    if not user_id:
        return BadRequest400Response("No such user")

    # Grab token(s)
    pg_result = psql(
        "SELECT token FROM token WHERE user_id=%s AND type='EMAIL_TOKEN_ACTIVATE'",
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
    _ = psql(
        """
UPDATE
  email
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
    _ = psql(
        """
DELETE FROM token
WHERE user_id = %s
  AND type = 'EMAIL_TOKEN_ACTIVATE'
RETURNING
  user_id
        """,
        [user_id],
    )
    # TODO: send welcome email?
    return Success200Response(data={"message": "Successfully activated"})


@auth
def get_email_change(
    request: sanic.Request, level: int = AUTH_LEVEL_UNCONFIRMED, user_id: int = -65536
) -> sanic.HTTPResponse:
    _: str = request.args["email"]
    password: str = request.args["password"]

    # Require additional password check
    if not cmp_pass(user_id, password):
        return Unauthenticated401Response("Invalid password")

    # TODO: implement
    # return NotImplemented501Response(data={"email": email})
    return NotImplemented501Response()


@auth
def get_password_change(
    request: sanic.Request, level: int = AUTH_LEVEL_UNCONFIRMED, user_id: int = -65536
) -> sanic.HTTPResponse:
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
    # TODO: Unable to resolve column 'user_id'
    psql(
        'UPDATE "user" SET passwd = %s WHERE id=%s RETURNING id',
        [passwd, user_id],
    )

    # TODO: return a message?
    return Success200Response()


def post_username_forgot(request: sanic.Request) -> sanic.HTTPResponse:
    return NotImplemented501Response()


def post_password_new_request(request: sanic.Request) -> sanic.HTTPResponse:
    return NotImplemented501Response()


def post_password_new_reset(request: sanic.Request) -> sanic.HTTPResponse:
    return NotImplemented501Response()


# ---------------
# File a report
# ---------------
@auth
def post_report(
    request: sanic.Request, level: int = AUTH_LEVEL_UNCONFIRMED, user_id: int = -65536
) -> sanic.HTTPResponse:
    """
    Used for submitting bug reports over CLI, web, or Android
    """

    client_app_name = request.json["clientAppName"]
    client_app_version = request.json["clientAppVersion"]
    client_app_release = request.json["clientAppRelease"]
    client_info = dict(request.json["clientInfo"])

    # TODO: use library wrapper or similar to generate mismatch in number of args
    psql(
        """
INSERT INTO bug (client_app_name, "version", "release", client_info)
  VALUES (%s, %s, %s)
RETURNING
  id, guid
        """,
        [client_app_name, client_app_version, client_app_release, client_info],
    )

    return Success200Response()
