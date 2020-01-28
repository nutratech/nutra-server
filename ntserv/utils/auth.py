from datetime import datetime

import jwt

from ..settings import JWT_SECRET as secret


# -----------------------------
# Authorization levels
# -----------------------------
AUTH_LEVEL_UNAUTHED = -10
AUTH_LEVEL_READ_ONLY = 0
AUTH_LEVEL_UNCONFIRMED = 10
AUTH_LEVEL_BASIC = 20
AUTH_LEVEL_PAID = 30
AUTH_LEVEL_TRAINER = 40
# -----------------------------


def auth_level(username, password):

    # TODO - report/handle:   jwt.exceptions.InvalidSignatureError

    # Get hash (if username exists)
    pg_result = psql("SELECT passwd FROM users WHERE username=%s", [username])

    #
    # ERROR: No such user
    if pg_result.err_msg:
        return pg_result.Response

    #
    # Compare password
    passwd = pg_result.row["passwd"]
    result = bcrypt.checkpw(password.encode(), passwd.encode())

    # Invalid password
    if not result:
        return None, AUTH_LEVEL_READ_ONLY, f"Invalid password for: {username}"
        # return Response(data={"error": f"Invalid password for: {username}"}, code=400)

    #
    # Create token
    try:
        token = jwt.decode(token, secret)
        print(token)
    except Exception as e:
        return None, AUTH_LEVEL_READ_ONLY, repr(e)

    # return {'id': user_id, 'auth-level': auth_level}


def issue_token():

    # TODO: make auth_level dynamic
    auth_level = AUTH_LEVEL_BASIC

    expires_at = datetime.now() + TOKEN_EXPIRY
    token = jwt.encode(
        {
            "username": username,
            "auth-level": auth_level,
            "expires": int(expires_at.timestamp()),
        },
        JWT_SECRET,
        algorithm="HS256",
    ).decode()

    return turn
