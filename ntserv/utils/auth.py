import traceback
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple

import bcrypt
import jwt
import sanic

from ntserv.env import JWT_SECRET, TOKEN_EXPIRY
from ntserv.persistence.psql import psql
from ntserv.utils.libserver import Unauthenticated401Response
from ntserv.utils.logger import get_logger

_logger = get_logger(__name__)

# -----------------------------
# Authorization levels
# -----------------------------
AUTH_LEVEL_UNAUTHED = -10
AUTH_LEVEL_READ_ONLY = 0
AUTH_LEVEL_UNCONFIRMED = 10
AUTH_LEVEL_BASIC = 20
AUTH_LEVEL_PAID = 30
AUTH_LEVEL_TRAINER = 40
AUTH_LEVEL_FULL_ADMIN = 10000


class AuthResult:
    def __init__(self, token: dict, err_msg: str = str()) -> None:
        self.user_id: int = token["id"]

        self.auth_level: int = token["auth-level"]
        self.expires: float = token["expires"]

        self.err_msg: str = err_msg

    @property
    def expired(self) -> bool:
        return datetime.now().timestamp() > self.expires


def issue_jwt_token(user_id: int, password: str) -> tuple:
    """Returns tuple: (token, auth_level, err_msg)"""

    # --------------------------------------------
    # Get hash
    # --------------------------------------------
    pg_result = psql("SELECT passwd FROM users WHERE id=%s", [user_id])

    # --------------------------------------------
    # Compare password
    # --------------------------------------------
    passwd = pg_result.row["passwd"]
    result = bcrypt.checkpw(password.encode(), passwd.encode())

    # Invalid password
    if not result:
        return None, AUTH_LEVEL_UNAUTHED, "Invalid password and username combination"

    # --------------------------------------------
    # Create token
    # --------------------------------------------
    try:
        return get_auth_level(user_id)
    except Exception as err:
        _logger.debug(traceback.format_exc())
        return None, AUTH_LEVEL_READ_ONLY, repr(err)


def get_auth_level(user_id: int) -> tuple:
    """Returns same tuple: (token, auth_level, error)"""

    # NOTE: is this the right level to start with here?
    auth_level = AUTH_LEVEL_UNCONFIRMED

    # --------------------------------------------
    # Check if email activated
    # --------------------------------------------
    pg_result = psql(
        "SELECT email FROM emails WHERE user_id=%s AND activated='t'", [user_id]
    )
    try:
        # FIXME: this is unused, email
        _ = pg_result.row["email"]
    except Exception as err:
        _logger.debug(traceback.format_exc())
        return jwt_token(user_id, auth_level), auth_level, repr(err)

    # pass: email active
    auth_level = AUTH_LEVEL_BASIC

    # --------------------------------------------
    # Check if admin
    # --------------------------------------------
    # TODO: is this the best practice, best way to verify admins? Is this documented?
    admin_ids = {1, 2}
    if user_id in admin_ids:
        auth_level = AUTH_LEVEL_FULL_ADMIN

    # Made it this far... create token
    return jwt_token(user_id, auth_level), auth_level, None


def jwt_token(user_id: int, auth_level: int) -> str:
    """Creates a JWT (token) for subsequent authorized requests"""

    expires_at = datetime.now() + TOKEN_EXPIRY
    token = jwt.encode(
        {
            "userId": user_id,
            "authLevel": AUTH_LEVEL_BASIC,
            "expiresAt": int(expires_at.timestamp()),
        },
        JWT_SECRET,
        algorithm="HS256",
    )

    return token


def check_token(_token: str) -> Tuple[AuthResult, str]:
    """Checks auth level from pre-issued token"""

    try:
        token = jwt.decode(_token, JWT_SECRET, algorithms=["HS256"])
        auth_result = AuthResult(token)
        error = str()

        if auth_result.expired:
            error = "LOGIN_TOKEN_EXPIRED"
        return auth_result, error

    except jwt.DecodeError as decode_err:
        _logger.debug(traceback.format_exc())
        return AuthResult({}), repr(decode_err)


def check_request(request: sanic.Request) -> Tuple[AuthResult, str]:
    try:
        token = request.headers["authorization"].split()[1]
        return check_token(token)

    # TODO: check for other types of exceptions that can be thrown?
    except (KeyError, jwt.DecodeError) as err:
        _logger.debug(traceback.format_exc())
        return AuthResult({}), repr(err)


# ------------------------------------------------
# Auth Decorator
# ------------------------------------------------
# TODO: handle level with **kwargs?
def auth(
    og_func: Callable[..., sanic.HTTPResponse],
    level: int = AUTH_LEVEL_UNAUTHED,
) -> Callable[..., sanic.HTTPResponse]:
    """Auth decorator, use to send 401s"""

    def func(request: sanic.Request) -> sanic.HTTPResponse:
        # Check authorization
        authr, err_msg = check_request(request)
        if not authr or authr.expired or authr.auth_level < AUTH_LEVEL_UNCONFIRMED:
            return Unauthenticated401Response(err_msg)

        # Execute original function
        return og_func(request, user_id=authr.user_id)

    # Returns a function
    return func
