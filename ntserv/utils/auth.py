import traceback
from datetime import datetime

import bcrypt
import jwt

from ..libserver import Unauthenticated401Response
from ..postgres import psql
from ..settings import JWT_SECRET, TOKEN_EXPIRY

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
# -----------------------------


def issue_jwt_token(user_id, password):
    """Returns tuple: (token, auth_level, error)"""

    # Get hash
    pg_result = psql("SELECT passwd FROM users WHERE id=%s", [user_id])

    #
    # Compare password
    passwd = pg_result.row["passwd"]
    result = bcrypt.checkpw(password.encode(), passwd.encode())

    # Invalid password
    if not result:
        return None, AUTH_LEVEL_UNAUTHED, "Invalid password and username combination"

    #
    # Create token
    try:
        return auth_level(user_id)
    except Exception as e:
        # traceback.print_stack(e)
        return None, AUTH_LEVEL_READ_ONLY, repr(e)


def auth_level(user_id):
    """Returns same tuple: (token, auth_level, error)"""

    auth_level = AUTH_LEVEL_UNCONFIRMED

    #
    # Check if email activated
    pg_result = psql(
        "SELECT email FROM emails WHERE user_id=%s AND activated='t'", [user_id]
    )
    try:
        email = pg_result.row["email"]
    except Exception as e:
        return jwt_token(user_id, auth_level), auth_level, repr(e)
    # pass: email active
    auth_level = AUTH_LEVEL_BASIC

    #
    # Check if paid member
    pass

    #
    # Check if paid trainer
    pass

    #
    # Check if administrator
    admin_ids = {1, 2}
    if user_id in admin_ids:
        auth_level = AUTH_LEVEL_FULL_ADMIN

    # Made it this far.. create token
    return jwt_token(user_id, auth_level), auth_level, None


def jwt_token(user_id, auth_level):
    """Creates a JWT (token) for subsequent authorized requests"""

    expires_at = datetime.now() + TOKEN_EXPIRY
    token = jwt.encode(
        {
            "id": user_id,
            "auth-level": AUTH_LEVEL_BASIC,
            "expires": int(expires_at.timestamp()),
        },
        JWT_SECRET,
        algorithm="HS256",
    ).decode()

    return token


def check_token(token):
    """Checks auth level from pre-issued token"""

    try:
        token = jwt.decode(token, JWT_SECRET, algorithm="HS256")
        auth_result = AuthResult(token)
        error = None
        if auth_result.expired:
            error = "LOGIN_TOKEN_EXPIRED"
        return auth_result, error
    except Exception as e:
        return None, repr(e)


def check_request(request):
    try:
        token = request.headers["authorization"].split()[1]
        return check_token(token)
    except Exception as e:
        return None, repr(e)


class AuthResult:
    def __init__(self, token):
        self.id = token["id"]
        self.auth_level = token["auth-level"]
        self.expires = token["expires"]
        self.expired = datetime.now().timestamp() > self.expires


"""
---------------------
Auth Decorator
---------------------
"""


def auth(og_func, level=None):
    """Auth decorator, use to send 401s"""

    def func(request):
        # Check authorization
        authr, err_msg = check_request(request)
        if not authr or authr.expired or authr.auth_level < AUTH_LEVEL_UNCONFIRMED:
            return Unauthenticated401Response(err_msg)

        # Execute original function
        return og_func(request, user_id=authr.id)

    # Returns a function
    return func
