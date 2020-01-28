import re
from datetime import datetime

import bcrypt
import jwt
import stripe

from .libserver import Response
from .postgres import psql
from .settings import JWT_SECRET, STRIPE_API_KEY, TOKEN_EXPIRY
from .utils.auth import AUTH_LEVEL_BASIC, auth_level as al

# Set Stripe API key
stripe.api_key = STRIPE_API_KEY


def POST_register(request):

    # Parse incoming request
    body = request.json
    username = body["username"]
    email = body["email"]
    password = body["password"]
    password_confirm = body["password-confirm"]

    # TODO: break up below block into "service-level" function

    """
    -------------------------------------
    Registration validation checks
    -------------------------------------

    Python regex:
        https://www.tutorialspoint.com/How-to-match-any-one-uppercase-character-in-python-using-Regular-Expression
        https://www.tutorialspoint.com/How-to-check-if-a-string-contains-only-upper-case-letters-in-Python
    """

    #
    # Username
    if (
        len(username) < 6
        or len(username) > 18
        or not re.match("^[0-9a-z_]+$", username)
    ):
        return Response(
            data={
                "error": "Username must be between 6 an 18 characters and contain only lowercase letters, numbers, and underscores"
            },
            code=400,
        )
    #
    # Password
    elif password_confirm != password:
        return Response(data={"error": "Passwords do NOT match"}, code=400)
    elif (
        len(password) < 6
        or len(password) > 18
        or not re.findall(r"""[~`!#$%\^&*+=\-\[\]\\',/{}|\\":<>\?]""", password)
        or not re.findall("[a-z]", password)
        or not re.findall("[A-Z]", password)
    ):
        return Response(
            data={
                "error": "Password must be 6-18 chars long, and contain both uppercase, lowercase, and a special character",
            },
            code=400,
        )

    #
    # Email
    elif not re.match(
        r"""^(([^<>()\[\]\\.,:\s@"]+(\.[^<>()\[\]\\.,:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$""",
        email,
    ):
        return Response(data={"error": "Email invalid"}, code=400)

    """
    -------------------------------------
    Attempt to SQL insert user
    -------------------------------------
    """

    # TODO: transactional `block()`
    stripe_id = stripe.Customer.create(email=email).id
    passwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    pg_result = psql(
        "INSERT INTO users (username, passwd, unverified_email, stripe_id) VALUES (%s, %s, %s, %s)",
        [username, passwd, email, stripe_id],
    )

    #
    # ERRORs
    if pg_result.err_msg:
        return pg_result.Response

    return Response(data={"message": "Successfully registered"})


def POST_login(request):

    # Parse incoming request
    username = request.json["username"]
    password = request.json["password"]

    token, auth_level, error = al(username, password)

    if token:
        return Response(data={"token": token, "auth-level": auth_level})
    else:
        return Response(data={"error": error, "auth-level": auth_level}, code=400)


"""
-------------------------
User-Trainer functions
-------------------------
"""


def GET_trainer_users(request):

    # TODO: get dynamically off token
    trainer_id = 5

    pg_result = psql("SELECT * FROM get_trainer_users(%s)", [trainer_id])

    return Response(data=pg_result.rows)


def GET_user_trainers(request):

    # TODO: get dynamically off token
    user_id = 5

    pg_result = psql("SELECT * FROM get_user_trainers(%s)", [user_id])

    return Response(data=pg_result.rows)


"""
-------------------------
Private DB functions
-------------------------
"""


def GET_favorites(request):

    # TODO: get dynamically off token
    user_id = 5

    pg_result = psql("SELECT * FROM get_user_favorite_foods(%s)", [user_id])

    return Response(data=pg_result.rows)


def GET_logs(request):

    # TODO: get dynamically off token
    user_id = 5

    pg_result = psql("SELECT * FROM food_logs WHERE user_id=%s", [user_id])

    return Response(data=pg_result.rows)


def GET_biometric(request):

    # TODO: get dynamically off token
    user_id = 5

    pg_result = psql("SELECT * FROM biometric_logs WHERE user_id=%s", [user_id])

    return Response(data=pg_result.rows)


def GET_exercise_log(request):

    # TODO: get dynamically off token
    user_id = 5

    pg_result = psql("SELECT * FROM exercise_logs WHERE user_id=%s", [user_id])

    return Response(data=pg_result.rows)


def GET_rdas(request):

    # TODO: get dynamically off token
    user_id = 5

    pg_result = psql("SELECT * FROM get_user_rdas(%s)", [user_id])

    return Response(data=pg_result.rows)


def GET_recipes(request):

    # TODO: get dynamically off token
    user_id = 5

    pg_result = psql("SELECT * FROM recipe_des WHERE user_id=%s", [user_id])

    return Response(data=pg_result.rows)
