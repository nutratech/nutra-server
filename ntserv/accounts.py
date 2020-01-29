import re
import uuid
from datetime import datetime

import bcrypt
import jwt
import stripe

from .libserver import Response
from .postgres import psql
from .settings import JWT_SECRET, STRIPE_API_KEY
from .utils import cache
from .utils.account import send_activation_email, user_id_from_username
from .utils.auth import (
    AUTH_LEVEL_BASIC,
    AUTH_LEVEL_READ_ONLY,
    AUTH_LEVEL_UNCONFIRMED,
    authdecorator,
    check_request,
    issue_token,
)

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
                "error": "Username must be 6-18 chars, and contain only lowercase letters, numbers, and underscores"
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
                "error": "Password must be 6-18 chars long, and contain an uppercase, a lowercase, and a special character",
            },
            code=400,
        )

    #
    # Email
    elif not re.match(
        r"""^(([^<>()\[\]\\.,:\s@"]+(\.[^<>()\[\]\\.,:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$""",
        email,
    ):
        return Response(data={"error": "Email address not recognizable"}, code=400)

    # -------------------------------------
    # Attempt to SQL insert user
    # -------------------------------------

    # Check if user has Stripe with us
    if email in cache.customers:
        stripe_id = cache.customers[email].id
    else:
        stripe_id = stripe.Customer.create(email=email).id
    # TODO: transactional `block()`
    # Insert user
    passwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    pg_result = psql(
        "INSERT INTO users (username, passwd, stripe_id) VALUES (%s, %s, %s) RETURNING id",
        [username, passwd, stripe_id],
    )
    # ERRORs
    if pg_result.err_msg:
        return pg_result.Response
    user_id = pg_result.row["id"]
    #
    # Insert emails
    pg_result = psql(
        "INSERT INTO emails (user_id, email) VALUES (%s, %s) RETURNING email",
        [user_id, email],
    )
    # ERRORs
    if pg_result.err_msg:
        psql("DELETE FROM users WHERE id=%s RETURNING product_id", [user_id])
        return pg_result.Response  #
    #
    # Insert tokens
    token = str(uuid.uuid4()).replace("-", "")
    send_activation_email(email, token)
    pg_result = psql(
        "INSERT INTO tokens (user_id, token, type) VALUES (%s, %s, %s) RETURNING token",
        [user_id, token, "email_token_activate"],
    )
    # ERRORs
    if pg_result.err_msg:
        psql("DELETE FROM users WHERE id=%s RETURNING product_id", [user_id])
        return pg_result.Response

    return Response(data={"message": "Successfully registered"})


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


def GET_user_details(request):

    # TODO: get dynamically off token
    user_id = 1
    pg_result = psql("SELECT * FROM get_user_details(%s)", [user_id])
    return Response(data=pg_result.rows)


"""
-------------------------
User-Trainer functions
-------------------------
"""


def GET_trainer_users(request):

    # TODO: get dynamically off token
    trainer_id = 1
    pg_result = psql("SELECT * FROM get_trainer_users(%s)", [trainer_id])
    return Response(data=pg_result.rows)


def GET_user_trainers(request):

    # TODO: get dynamically off token
    user_id = 1
    pg_result = psql("SELECT * FROM get_user_trainers(%s)", [user_id])
    return Response(data=pg_result.rows)


"""
-------------------------
Private DB functions
-------------------------
"""


# @customannotation(auth=AUTH_LEVEL_BASIC)
# @authdecorator(self, request)
def GET_favorites(request):
    authr, error = check_request(request)
    if not authr or authr.expired or authr.auth_level < AUTH_LEVEL_UNCONFIRMED:
        return Response(data={"error": error}, code=401)

    pg_result = psql("SELECT * FROM get_user_favorite_foods(%s)", [authr.id])
    return Response(data=pg_result.rows)


def POST_favorites(request):
    authr, error = check_request(request)
    if not authr or authr.expired or authr.auth_level < AUTH_LEVEL_BASIC:
        return Response(data={"error": error}, code=401)

    # Attempt insert
    food_id = request.json["food_id"]
    pg_result = psql(
        "INSERT INTO favorite_foods (user_id, food_id) VALUES (%s, %s) RETURNING created_at",
        [authr.id, food_id],
    )

    # ERROR: Duplicate?
    if pg_result.err_msg:
        return Response(data={"error": pg_result.err_msg}, code=400)
    return Response()


def DEL_favorites(request):
    authr, error = check_request(request)
    if not authr or authr.expired or authr.auth_level < AUTH_LEVEL_BASIC:
        return Response(data={"error": error}, code=401)

    # Attempt insert
    food_id = request.json["food_id"]
    pg_result = psql(
        "DELETE FROM favorite_foods WHERE user_id=%s AND food_id=%s RETURNING food_id",
        [authr.id, food_id],
    )

    # ERROR: Duplicate?
    if pg_result.err_msg:
        return Response(data={"error": pg_result.err_msg}, code=400)
    return Response()


def GET_logs(request):

    # TODO: get dynamically off token
    user_id = 1
    pg_result = psql("SELECT * FROM food_logs WHERE user_id=%s", [user_id])
    return Response(data=pg_result.rows)


def GET_biometric(request):

    # TODO: get dynamically off token
    user_id = 1
    pg_result = psql("SELECT * FROM biometric_logs WHERE user_id=%s", [user_id])
    return Response(data=pg_result.rows)


def GET_exercise_log(request):

    # TODO: get dynamically off token
    user_id = 1
    pg_result = psql("SELECT * FROM exercise_logs WHERE user_id=%s", [user_id])
    return Response(data=pg_result.rows)


def GET_rdas(request):

    # TODO: get dynamically off token
    user_id = 1
    pg_result = psql("SELECT * FROM get_user_rdas(%s)", [user_id])
    return Response(data=pg_result.rows)


def GET_recipes(request):

    # TODO: get dynamically off token
    user_id = 1
    pg_result = psql("SELECT * FROM recipe_des WHERE user_id=%s", [user_id])
    return Response(data=pg_result.rows)
