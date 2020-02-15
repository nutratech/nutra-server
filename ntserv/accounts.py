import re
import uuid
from datetime import datetime

import bcrypt
import jwt
import stripe
from dateutil.parser import parse as parse_datetime

from .libserver import Response
from .postgres import psql
from .settings import CUSTOM_FOOD_DATA_SRC_ID, JWT_SECRET, STRIPE_API_KEY
from .utils import cache
from .utils.account import (
    cmp_pass,
    send_activation_email,
    user_id_from_unver_email,
    user_id_from_username,
)
from .utils.auth import (
    AUTH_LEVEL_BASIC,
    AUTH_LEVEL_PAID,
    AUTH_LEVEL_READ_ONLY,
    AUTH_LEVEL_TRAINER,
    AUTH_LEVEL_UNCONFIRMED,
    auth,
    check_request,
    issue_token,
    jwt_token,
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
    # TODO: transactional `block()`
    # CREATE USER
    passwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
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
    pg_result = psql("SELECT * FROM get_user_details(%s)", [user_id])
    return Response(data=pg_result.rows)


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
    return Response(code=501)


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


"""
-------------------------
User-Trainer functions
-------------------------
"""


@auth
def OPT_users_trainers(request, level=AUTH_LEVEL_BASIC, user_id=None):
    method = request.environ["REQUEST_METHOD"]

    if method == "GET":
        pg_result = psql("SELECT * FROM get_user_trainers(%s)", [user_id])
        return Response(data=pg_result.rows)

    # Approve trainer
    elif method == "POST":
        trainer_id = request.json["trainer_id"]
        pg_result = psql(
            "UPDATE trainer_users SET approved='t' WHERE user_id=%s AND trainer_id=%s) RETURNING trainer_id",
            [user_id, trainer_id],
        )
        return Response(data=pg_result.rows)

    # Remove trainer
    elif method == "DELETE":
        trainer_id = request.json["trainer_id"]
        pg_result = psql(
            "DELETE FROM trainer_users WHERE user_id=%s AND trainer_id=%s RETURNING trainer_id",
            [user_id, trainer_id],
        )
        return Response(data=pg_result.rows)


@auth
def OPT_trainers_users(request, level=AUTH_LEVEL_TRAINER, user_id=None):
    method = request.environ["REQUEST_METHOD"]

    if method == "GET":
        pg_result = psql("SELECT * FROM get_trainer_users(%s)", [user_id])
        return Response(data=pg_result.rows)

    # Add client to trainer
    elif method == "POST":
        client_id = request.json["user_id"]
        pg_result = psql(
            "INSERT INTO trainer_users (trainer_id, user_id) VALUES (%s, %s) RETURNING user_id",
            [user_id, client_id],
        )
        return Response(data=pg_result.rows)

    # Remove client
    elif method == "DELETE":
        client_id = request.json["user_id"]
        pg_result = psql(
            "DELETE FROM trainer_users WHERE trainer_id=%s AND user_id=%s RETURNING user_id",
            [user_id, client_id],
        )
        return Response(data=pg_result.rows)


@auth
def POST_trainers_switch(request, level=AUTH_LEVEL_TRAINER, user_id=None):
    client_id = request.json["user_id"]
    pg_result = psql(
        "SELECT user_id FROM trainer_users WHERE trainer_id=%s AND user_id=%s AND approved='t'",
        [user_id, client_id],
    )
    # Check if valid
    if not pg_result.rows:
        return Response(data={"error": "No such approved user"}, code=401)

    # Trainer can do everything unconfirmed member can do
    token = jwt_token(client_id, AUTH_LEVEL_UNCONFIRMED)
    return Response(data={"token": token})


"""
-------------------------
Private DB functions
-------------------------
"""


@auth
def OPT_favorites(request, level=AUTH_LEVEL_BASIC, user_id=None):
    method = request.environ["REQUEST_METHOD"]
    if method == "GET":
        pg_result = psql("SELECT * FROM get_user_favorite_foods(%s)", [user_id])
        return Response(data=pg_result.rows)

    # Attempt insert
    elif method == "POST":
        food_id = request.json["food_id"]
        pg_result = psql(
            "INSERT INTO favorite_foods (user_id, food_id) VALUES (%s, %s) RETURNING created_at",
            [user_id, food_id],
        )

        # ERROR: Duplicate?
        if pg_result.err_msg or not pg_result.rows:
            return Response(data={"error": pg_result.err_msg}, code=400)
        return Response()

    # Attempt removal
    elif method == "DELETE":
        food_id = request.json["food_id"]
        pg_result = psql(
            "DELETE FROM favorite_foods WHERE user_id=%s AND food_id=%s RETURNING food_id",
            [user_id, food_id],
        )

        # ERROR: doesn't exist?
        if pg_result.err_msg or not pg_result.rows:
            return Response(data={"error": pg_result.err_msg}, code=400)
        return Response()


@auth
def OPT_logs_food(request, level=AUTH_LEVEL_BASIC, user_id=None):
    method = request.environ["REQUEST_METHOD"]
    if method == "GET":
        pg_result = psql("SELECT * FROM food_logs WHERE user_id=%s", [user_id])
        return Response(data=pg_result.rows)

    # Add to log
    elif method == "POST":
        meal_name = request.json["meal_name"]
        amount = request.json["amount"]

        msre_id = request.json.get("msre_id")
        food_id = request.json.get("food_id")
        recipe_id = request.json.get("recipe_id")
        eat_on_date = parse_datetime(request.json["eat_on_date"])

        if food_id:
            # Add food to log
            pg_result = psql(
                "INSERT INTO food_logs (user_id, eat_on_date, meal_name, amount, msre_id, food_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                [user_id, eat_on_date, meal_name, amount, msre_id, food_id],
            )
            return Response(data=pg_result.row)
        elif recipe_id:
            # Add recipe to log
            pg_result = psql(
                "INSERT INTO food_logs (user_id, eat_on_date, meal_name, amount, recipe_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                [user_id, eat_on_date, meal_name, amount, recipe_id],
            )
            return Response(data=pg_result.row)
        else:
            return Response(data={"error": "No food or recipe specified"}, code=400)

    # Remove from log
    elif method == "DELETE":
        id = request.json["id"]
        pg_result = psql(
            "DELETE FROM food_logs WHERE user_id=%s and id=%s RETURNING id",
            [user_id, id],
        )
        # Failed to delete, probably doesn't exist or isn't ours
        if not pg_result.rows:
            return Response(code=400)
        return Response()


@auth
def OPT_logs_exercise(request, level=AUTH_LEVEL_BASIC, user_id=None):
    method = request.environ["REQUEST_METHOD"]
    if method == "GET":
        pg_result = psql("SELECT * FROM exercise_logs WHERE user_id=%s", [user_id])
        return Response(data=pg_result.rows)

    # Add to log
    elif method == "POST":
        exercise_id = request.json["exercise_id"]
        date = request.json["date"]

        reps = request.json.get("reps")
        weight = request.json.get("weight")
        duration_min = request.json.get("duration_min")

        if reps and weight:
            pg_result = psql(
                "INSERT INTO exercise_logs (user_id, exercise_id, date, reps, weight) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                [user_id, exercise_id, date, reps, weight],
            )
            id = pg_result.row["id"]
            return Response(data=id)
        elif duration_min:
            pg_result = psql(
                "INSERT INTO exercise_logs (user_id, exercise_id, date, duration_min) VALUES (%s, %s, %s, %s) RETURNING id",
                [user_id, exercise_id, date, duration_min],
            )
            id = pg_result.row["id"]
            return Response(data=id)
        else:
            return Response(
                data={"error": "Not enough info to create exericse log item"}, code=400
            )

    # Remove from log
    elif method == "DELETE":
        id = request.json["id"]
        pg_result = psql(
            "DELETE FROM exercise_logs WHERE user_id=%s and id=%s RETURNING id",
            [user_id, id],
        )
        # Failed to delete, probably doesn't exist or isn't ours
        if not pg_result.rows:
            return Response(code=400)
        return Response()


@auth
def OPT_logs_biometric(request, level=AUTH_LEVEL_BASIC, user_id=None):
    method = request.environ["REQUEST_METHOD"]
    if method == "GET":
        pg_result = psql("SELECT * FROM biometric_logs WHERE user_id=%s", [user_id])
        return Response(data=pg_result.rows)

    # Add to log
    elif method == "POST":
        meal_name = request.json["meal_name"]
        amount = request.json["amount"]
        msre_id = request.json["msre_id"]

        food_id = request.json.get("food_id")
        recipe_id = request.json.get("recipe_id")
        eat_on_date = parse_datetime(request.json["eat_on_date"])

        if food_id:
            # Add food to log
            pg_result = psql(
                "INSERT INTO food_logs (user_id, eat_on_date, meal_name, amount, msre_id, food_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                [user_id, eat_on_date, meal_name, amount, msre_id, food_id],
            )
            return Response(data=pg_result.row)
        elif recipe_id:
            # Add recipe to log
            pg_result = psql(
                "INSERT INTO food_logs (user_id, eat_on_date, meal_name, amount, recipe_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                [user_id, eat_on_date, meal_name, amount, recipe_id],
            )
            return Response(data=pg_result.row)
        else:
            return Response(data={"error": "No food or recipe specified"}, code=400)

    # Remove from log
    elif method == "DELETE":
        id = request.json["id"]
        pg_result = psql(
            "DELETE FROM food_logs WHERE user_id=%s and id=%s RETURNING id",
            [user_id, id],
        )
        # Failed to delete, probably doesn't exist or isn't ours
        if not pg_result.rows:
            return Response(code=400)
        return Response()


@auth
def GET_logs_biometric(request, level=AUTH_LEVEL_UNCONFIRMED, user_id=None):
    pg_result = psql("SELECT * FROM biometric_logs WHERE user_id=%s", [user_id])
    return Response(data=pg_result.rows)


@auth
def GET_logs_exercise(request, level=AUTH_LEVEL_UNCONFIRMED, user_id=None):
    pg_result = psql("SELECT * FROM exercise_logs WHERE user_id=%s", [user_id])
    return Response(data=pg_result.rows)


@auth
def OPT_rdas(request, level=AUTH_LEVEL_BASIC, user_id=None):
    method = request.environ["REQUEST_METHOD"]

    if method == "GET":
        pg_result = psql("SELECT * FROM get_user_rdas(%s)", [user_id])
        return Response(data=pg_result.rows)

    elif method == "POST":
        nutr_id = request.json["nutr_id"]
        rda = request.json["rda"]
        # TODO - ask Kyle about this query
        pg_result = psql(
            "INSERT INTO rda (user_id, nutr_id, rda) VALUES (%s, %s, %s) ON CONFLICT ON CONSTRAINT rda_pkey DO UPDATE SET rda=excluded.rda WHERE rda.user_id=excluded.user_id AND rda.nutr_id=excluded.nutr_id RETURNING nutr_id",
            [user_id, nutr_id, rda],
        )
        return Response()

    elif method == "DELETE":
        nutr_id = request.json["nutr_id"]
        rda = request.json["rda"]
        pg_result = psql(
            "DELETE FROM rda WHERE user_id=%s AND nutr_id=%s RETURNING nutr_id",
            [user_id, nutr_id],
        )
        return Response()


@auth
def OPT_recipes(request, level=AUTH_LEVEL_BASIC, user_id=None):
    method = request.environ["REQUEST_METHOD"]

    if method == "GET":
        pg_result = psql("SELECT * FROM recipe_des WHERE user_id=%s", [user_id])
        return Response(data=pg_result.rows)

    elif method == "POST":
        # TODO: this
        return Response(code=501)

    elif method == "DELETE":
        recipe_id = request.json["recipe_id"]
        pg_result = psql(
            "DELETE FROM recipe_des WHERE user_id=%s AND recipe_id=%s RETURNING recipe_id",
            [user_id, recipe_id],
        )
        return Response()


@auth
def GET_recipes_foods(request, level=AUTH_LEVEL_UNCONFIRMED, user_id=None):
    recipe_ids = [int(x) for x in request.json["recipe_ids"].split(",")]
    pg_result = psql(
        "SELECT * FROM recipe_dat WHERE user_id=%s and recipe_id=any(%s)",
        [user_id, recipe_ids],
    )
    return Response(data=pg_result.rows)


@auth
def OPT_custom_foods(request, level=AUTH_LEVEL_BASIC, user_id=None):
    method = request.environ["REQUEST_METHOD"]

    if method == "GET":
        pg_result = psql("SELECT * FROM food_des WHERE user_id=%s", [user_id])
        return Response(data=pg_result.rows)

    elif method == "POST":
        long_desc = request.json["food_name"]
        tags = request.json["tags"]
        fdgrp_id = request.json["fdgrp_id"]
        shared = request.json["shared"]
        _nutrients = request.json["nutrients"]
        _servings = request.json["servings"]

        pg_result = psql(
            "INSERT INTO food_des (long_desc, fdgrp_id, data_src_id, user_id, shared) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            [long_desc, fdgrp_id, CUSTOM_FOOD_DATA_SRC_ID, user_id, shared],
        )
        id = pg_result.row["id"]
        # TODO - finish up
        return Response()

    elif method == "DELETE":
        food_id = request.json["food_id"]
        pg_result = psql(
            "DELETE FROM food_des WHERE user_id=%s AND food_id=%s RETURNING id",
            [user_id, food_id],
        )
        return Response()


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
