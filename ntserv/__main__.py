# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 18:20:27 2020

@author: shane
"""

import os

import gunicorn  # pylint: disable=unused-import
from flask import Flask, request, send_from_directory
from flask_cors import CORS

from ntserv.accounts import (
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
    POST_v2_login,
)
from ntserv.calculate import (
    GET_calc_bmr,
    GET_calc_bmr_cunningham,
    GET_calc_bmr_harris_benedict,
    GET_calc_bmr_katch_mcardle,
    GET_calc_bmr_mifflin_st_jeor,
    GET_calc_bodyfat,
    GET_calc_lblimits,
    GET_nutrients,
)
from ntserv.controllers.sync import OPT_sync
from ntserv.libserver import Request, home_page_text, self_route_rules
from ntserv.shop import (
    GET_categories,
    GET_products,
    GET_products_profits,
    OPT_addresses,
    OPT_orders,
    PATCH_orders_admin,
    POST_products_reviews,
    POST_shipping_esimates,
    POST_validate_addresses,
)
from ntserv.utils.cache import reload

# Load SQL cache in-memory, if accessible
reload()

# Export the Flask server for gunicorn
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
CORS(app)


# -------------------------
# Routes
# -------------------------

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


@app.route("/v2/login", methods=["POST"])
def post_v2_login():
    return Request(POST_v2_login, request)


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
# Sync functions
# -------------------------
@app.route("/sync", methods=["GET", "POST"])
def post_sync():
    return Request(OPT_sync, request)


# -------------------------
# Basic DB functions
# -------------------------
@app.route("/calc/bodyfat")
def get_calc_bodyfat():
    return Request(GET_calc_bodyfat, request)


@app.route("/calc/lblimits")
def get_calc_lblimits():
    return Request(GET_calc_lblimits, request)


@app.route("/calc/bmr")
def get_calc_bmr():
    return Request(GET_calc_bmr, request)


@app.route("/calc/bmr/katch_mcardle")
def get_calc_bmr_katch_mcardle():
    return Request(GET_calc_bmr_katch_mcardle, request)


@app.route("/calc/bmr/cunningham")
def get_calc_bmr_cunningham():
    return Request(GET_calc_bmr_cunningham, request)


@app.route("/calc/bmr/mifflin_st_jeor")
def get_calc_bmr_mifflin_st_jeor():
    return Request(GET_calc_bmr_mifflin_st_jeor, request)


@app.route("/calc/bmr/harris_benedict")
def get_calc_bmr_harris_benedict():
    return Request(GET_calc_bmr_harris_benedict, request)


###################################
# JSON routes (public DB functions)
@app.route("/nutrients")
def get_nutrients():
    return Request(GET_nutrients, request)


################################
# HTML routes for same functions
@app.route("/html/nutrients")
def get_html_nutrients():
    return Request(GET_nutrients, request, response_type="HTML")


# -------------------------
# Shop functions
# -------------------------
@app.route("/validate/addresses", methods=["POST"])
def post_validate_addresses():
    return Request(POST_validate_addresses, request)


@app.route("/shipping/estimates", methods=["POST"])
def post_shipping_methods():
    return Request(POST_shipping_esimates, request)


@app.route("/addresses", methods=["GET", "POST", "PATCH", "DELETE"])
def opt_addresses():
    return Request(OPT_addresses, request)


@app.route("/categories")
def get_categories():
    return Request(GET_categories, request)


@app.route("/products")
def get_products():
    return Request(GET_products, request)


@app.route("/orders", methods=["GET", "POST"])
def post_orders():
    return Request(OPT_orders, request)


@app.route("/products/reviews", methods=["POST"])
def post_products_reviews():
    return Request(POST_products_reviews, request)


@app.route("/report", methods=["POST"])
def post_report():
    return Request(POST_report, request)


# -------------------------
# Admin functions
# -------------------------
@app.route("/products/profits")
def get_products_profits():
    return Request(GET_products_profits, request)


@app.route("/orders/admin", methods=["PATCH"])
def patch_orders_admin():
    return Request(PATCH_orders_admin, request)
