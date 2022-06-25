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
    post_calc_1rm,
    post_calc_bmr,
    post_calc_body_fat,
    post_calc_lb_limits,
)
from ntserv.controllers.sync import OPT_sync
from ntserv.env import PROXY_SECRET
from ntserv.persistence.psql import get_pg_version
from ntserv.utils.cache import reload
from ntserv.utils.libserver import exc_req, home_page_text, self_route_rules

# Load SQL cache in-memory, if accessible
reload()

# Export the Sanic app
app = Sanic(__module__)
app.config.FORWARDED_SECRET = PROXY_SECRET


# TODO: blueprinting, e.g. /auth, /calc


# -------------------------
# Routes
# -------------------------
@app.route("/")
async def _(*args):
    _ = args
    url_map = self_route_rules(app)
    home_page = home_page_text(url_map)
    return html(f"<pre>{home_page}</pre>", 200)


@app.route("/user_details")
async def _(request):
    return exc_req(GET_user_details, request)


@app.route("/pg/version")
async def _(request):
    return exc_req(get_pg_version, request)


# ------------------------------------------------
# Public functions: /nutrients
# ------------------------------------------------
@app.route("/nutrients")
async def _get_nutrients(request):
    return exc_req(get_nutrients, request)


@app.route("/nutrients/html")
async def _get_nutrients_html(request):
    return exc_req(get_nutrients, request, response_type="HTML")


# ------------------------------------------------
# Public functions: /calc
# ------------------------------------------------
@app.route("/calc/1rm", methods=["POST"])
async def _(request):
    return exc_req(post_calc_1rm, request)


@app.route("/calc/bmr", methods=["POST"])
async def _(request):
    return exc_req(post_calc_bmr, request)


@app.route("/calc/body-fat", methods=["POST"])
async def _(request):
    return exc_req(post_calc_body_fat, request)


@app.route("/calc/lb-limits", methods=["POST"])
async def _(request):
    return exc_req(post_calc_lb_limits, request)


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
