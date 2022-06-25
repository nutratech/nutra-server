# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 18:20:27 2020

@author: shane
"""

from sanic import Sanic, html

from ntserv import __module__
from ntserv.controllers.accounts import (
    GET_confirm_email,
    GET_email_change,
    GET_password_change,
    GET_user_details,
    POST_login,
    POST_password_new_request,
    POST_password_new_reset,
    POST_register,
    POST_username_forgot,
    POST_v2_login,
)
from ntserv.controllers.calculate import (
    get_nutrients,
    post_calc_bmr,
    post_calc_bodyfat,
    post_calc_lblimits,
)
from ntserv.controllers.sync import OPT_sync
from ntserv.env import PROXY_SECRET
from ntserv.persistence.psql import get_test_pg_connect
from ntserv.utils.cache import reload
from ntserv.utils.libserver import exc_req, home_page_text, self_route_rules

# Load SQL cache in-memory, if accessible
reload()

# Export the Sanic app
app = Sanic(__module__)
app.config.FORWARDED_SECRET = PROXY_SECRET


# -------------------------
# Routes
# -------------------------
# TODO: use *args, **kwargs
# noinspection PyUnusedLocal
# pylint: disable=unused-argument
@app.route("/")
async def get_home_page(request):
    url_map = self_route_rules(app)
    home_page = home_page_text(url_map)
    return html(f"<pre>{home_page}</pre>", 200)


@app.route("/user_details")
async def get_user_details(request):
    return exc_req(GET_user_details, request)


@app.route("/pg/version")
async def _get_test_pg_connect(request):
    return exc_req(get_test_pg_connect, request)


# ------------------------------------------------
# Public functions: /calc
# ------------------------------------------------
@app.route("/calc/bodyfat", methods=["POST"])
async def _post_calc_bodyfat(request):
    return exc_req(post_calc_bodyfat, request)


@app.route("/calc/lblimits", methods=["POST"])
async def _post_calc_lblimits(request):
    return exc_req(post_calc_lblimits, request)


@app.route("/calc/bmr", methods=["POST"])
async def _post_calc_bmr(request):
    return exc_req(post_calc_bmr, request)


# -------------------------
# Account functions
# -------------------------
@app.route("/register", methods=["POST"])
async def post_register(request):
    return exc_req(POST_register, request)


@app.route("/login", methods=["POST"])
async def post_login(request):
    return exc_req(POST_login, request)


@app.route("/v2/login", methods=["POST"])
async def post_v2_login(request):
    return exc_req(POST_v2_login, request)


@app.route("/email/confirm")
async def get_confirm_email(request):
    return exc_req(GET_confirm_email, request)


@app.route("/email/change")
async def get_email_change(request):
    return exc_req(GET_email_change, request)


@app.route("/password/change")
async def get_change_password(request):
    return exc_req(GET_password_change, request)


@app.route("/username/forgot")
async def post_forgot_username(request):
    return exc_req(POST_username_forgot, request)


@app.route("/password/new/request")
async def post_password_new_request(request):
    return exc_req(POST_password_new_request, request)


@app.route("/password/new/reset")
async def post_password_new_reset(request):
    return exc_req(POST_password_new_reset, request)


# ------------------------------------------------
# Sync functions
# ------------------------------------------------
@app.route("/sync", methods=["GET", "POST"])
async def post_sync(request):
    return exc_req(OPT_sync, request)


# ------------------------------------------------
# Public functions: /nutrients
# ------------------------------------------------
@app.route("/nutrients")
async def _get_nutrients(request):
    return exc_req(get_nutrients, request)


@app.route("/nutrients/html")
async def _get_nutrients_html(request):
    return exc_req(get_nutrients, request, response_type="HTML")
