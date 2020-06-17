# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 18:20:27 2020

@author: shane
"""

import os

import gunicorn
from flask import Flask, request, send_from_directory
from flask_cors import CORS

from .accounts import (
    GET_confirm_email,
    GET_email_change,
    GET_password_change,
    GET_user_details,
    POST_login,
    POST_password_new_request,
    POST_password_new_reset,
    POST_register,
    POST_report,
    POST_username_forgot,
)
from .libserver import Request, home_page_text, self_route_rules
from .shop import (
    GET_countries,
    GET_products,
    GET_products__product_id__reviews,
    PATCH_orders_admin,
    POST_orders,
    POST_products_reviews,
    POST_shipping_esimates,
    POST_validate_addresses,
)
from .usda import (
    GET_calc_bodyfat,
    GET_calc_lblimits,
)
from .utils.cache import reload

# Load SQL cache in-memory
reload()

# Export the Flask server for gunicorn
app = Flask(__name__)
CORS(app)


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


@app.route("/favicon.ico")
def get_favicon_ico():
    return send_from_directory(
        os.path.join(os.path.dirname(app.root_path), "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


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
# Basic DB functions
# -------------------------
@app.route("/calc/bodyfat")
def get_calc_bodyfat():
    return Request(GET_calc_bodyfat, request)


@app.route("/calc/lblimits")
def get_calc_lblimits():
    return Request(GET_calc_lblimits, request)


# -------------------------
# Shop functions
# -------------------------
@app.route("/countries")
def get_countries():
    return Request(GET_countries, request)


@app.route("/shipping/estimates", methods=["POST"])
def post_shipping_methods():
    return Request(POST_shipping_esimates, request)


@app.route("/products")
def get_products():
    return Request(GET_products, request)


@app.route("/orders", methods=["POST"])
def post_orders():
    return Request(POST_orders, request)


@app.route("/orders/admin", methods=["PATCH"])
def patch_orders_admin():
    return Request(PATCH_orders_admin, request)


@app.route("/products/<id>/reviews")
def get_products__product_id__reviews(id):
    return Request(GET_products__product_id__reviews, request)


@app.route("/products/reviews", methods=["POST"])
def post_products_reviews():
    return Request(POST_products_reviews, request)


@app.route("/report", methods=["POST"])
def post_report():
    return Request(POST_report, request)
