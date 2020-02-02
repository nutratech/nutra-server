#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 18:20:27 2020

@author: shane
"""

import os
import subprocess
import threading

import gunicorn
from flask import Flask, request
from flask_cors import CORS

from ntserv.accounts import (
    GET_confirm_email,
    GET_email_change,
    GET_password_change,
    GET_recipes,
    GET_recipes_foods,
    GET_user_details,
    OPT_favorites,
    OPT_logs_biometric,
    OPT_logs_exercise,
    OPT_logs_food,
    OPT_rdas,
    OPT_trainers_users,
    OPT_users_trainers,
    POST_login,
    POST_password_new_request,
    POST_password_new_reset,
    POST_register,
    POST_report,
    POST_trainers_switch,
    POST_username_forgot,
)
from ntserv.libserver import Request, Response, home_page_text, self_route_rules
from ntserv.shop import (
    GET_plans,
    GET_products,
    GET_products__product_id__reviews,
    GET_products_avg_ratings,
    GET_skus,
    GET_stripe_plans,
    GET_stripe_products,
    GET_stripe_skus,
    POST_orders,
    POST_products_reviews,
)
from ntserv.usda import (
    GET_analyze,
    GET_biometrics,
    GET_data_src,
    GET_exercises,
    GET_fdgrp,
    GET_nutrients,
    GET_search,
    GET_serving_sizes,
    GET_sort,
)
from ntserv.utils.cache import reload
from ntserv.utils.caffeine import caffeinate

# Load SQL cache in-memory
reload()

# Export the Flask server for gunicorn
app = Flask(__name__)
CORS(app)
caffeinate()


"""
-------------------------
Routes
-------------------------
"""


@app.route("/")
def get_home_page():
    url_map = self_route_rules(app)
    home_page = home_page_text(url_map)
    return f"<pre>{home_page}</pre>"


@app.route("/user_details")
def get_user_details():
    return Request(GET_user_details, request)


# -------------------------
# Account functions
# -------------------------
@app.route("/register", methods=["POST"])
def post_register():
    return Request(POST_register, request)


@app.route("/login", methods=["POST"])
def post_login():
    return Request(POST_login, request)


@app.route("/email/confirm")
def get_confirm_email():
    return Request(GET_confirm_email, request)


@app.route("/email/change")
def get_email_change():
    return Request(GET_email_change, request)


@app.route("/password/change")
def get_change_password():
    return Request(GET_password_change, request)


@app.route("/username/forgot")
def post_forgot_username():
    return Request(POST_username_forgot, request)


@app.route("/password/new/request")
def post_password_new_request():
    return Request(POST_password_new_request, request)


@app.route("/password/new/reset")
def post_password_new_reset():
    return Request(POST_password_new_reset, request)


# -------------------------
# Trainer functions
# -------------------------
@app.route("/users/trainers", methods=["GET", "POST", "DELETE"])
def users_trainers():
    return Request(OPT_users_trainers, request)


@app.route("/trainers/users", methods=["GET", "POST", "DELETE"])
def trainer_users():
    return Request(OPT_trainers_users, request)


@app.route("/trainers/switch")
def post_trainers_switch():
    return Request(POST_trainers_switch, request)


# -------------------------
# Basic DB functions
# -------------------------
@app.route("/data_src")
def get_data_src():
    return Request(GET_data_src, request)


@app.route("/fdgrp")
def get_fdgrp():
    return Request(GET_fdgrp, request)


@app.route("/serving_sizes")
def get_serving_sizes():
    return Request(GET_serving_sizes, request)


@app.route("/nutrients")
def get_nutrients():
    return Request(GET_nutrients, request)


@app.route("/exercises")
def get_exercises():
    return Request(GET_exercises, request)


@app.route("/biometrics")
def get_biometrics():
    return Request(GET_biometrics, request)


@app.route("/search")
def get_search():
    return Request(GET_search, request)


@app.route("/sort")
def get_sort():
    return Request(GET_sort, request)


@app.route("/analyze")
def get_analyze():
    return Request(GET_analyze, request)


# -------------------------
# Private DB functions
# -------------------------
@app.route("/favorites", methods=["GET", "POST", "DELETE"])
def favorites():
    return Request(OPT_favorites, request)


@app.route("/recipes")
def get_recipes():
    return Request(GET_recipes, request)


@app.route("/recipes/foods")
def get_recipes_foods():
    return Request(GET_recipes_foods, request)


@app.route("/users/rdas", methods=["POST", "DELETE"])
def rdas():
    return Request(OPT_rdas, request)


@app.route("/logs/food", methods=["GET", "POST", "DELETE"])
def logs_food():
    return Request(OPT_logs_food, request)


@app.route("/logs/biometric", methods=["GET", "POST", "DELETE"])
def logs_biometric():
    return Request(OPT_logs_biometric, request)


@app.route("/logs/exercise", methods=["GET", "POST", "DELETE"])
def logs_exercise():
    return Request(OPT_logs_exercise, request)


@app.route("/report", methods=["POST"])
def post_report():
    return Request(POST_report, request)


# -------------------------
# Stripe functions
# -------------------------
@app.route("/products")
def get_products():
    return Request(GET_products, request)


@app.route("/skus")
def get_skus():
    return Request(GET_skus, request)


@app.route("/plans")
def get_plans():
    return Request(GET_plans, request)


@app.route("/stripe/products")
def get_stripe_products():
    return Request(GET_stripe_products, request)


@app.route("/stripe/skus")
def get_stripe_skus():
    return Request(GET_stripe_skus, request)


@app.route("/stripe/plans")
def get_stripe_plans():
    return Request(GET_stripe_plans, request)


@app.route("/orders", methods=["POST"])
def post_orders():
    return Request(POST_orders, request)


@app.route("/products/<id>/reviews")
def get_products__product_id__reviews(id):
    return Request(GET_products__product_id__reviews, request)


@app.route("/products/reviews", methods=["POST"])
def post_products_reviews():
    return Request(POST_products_reviews, request)


@app.route("/products/avg_ratings")
def get_products_avg_ratings():
    return Request(GET_products_avg_ratings, request)


#
# Make script executable
if __name__ == "__main__":
    """ Run as file (or debug it in vscode!) """

    print("[__main__] bypassing gunicorn...")
    port = int(os.getenv("PORT", 20000))
    app.run(
        host="127.0.0.1", port=port, debug=True,
    )
