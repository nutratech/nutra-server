# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 18:20:27 2020

@author: shane
"""
import sanic
from sanic_ext import Extend

from ntserv import ALLOWED_ORIGINS, __module__
from ntserv.controllers.accounts import (
    get_confirm_email,
    get_email_change,
    get_password_change,
    get_user_details,
    post_login,
    post_password_new_request,
    post_password_new_reset,
    post_register,
    post_username_forgot,
    post_v2_login,
)
from ntserv.controllers.calculate import (
    get_nutrients,
    post_calc_1rm,
    post_calc_bmr,
    post_calc_body_fat,
    post_calc_lb_limits,
)
from ntserv.controllers.sync import opt_sync
from ntserv.env import PROXY_SECRET
from ntserv.persistence.psql import get_pg_version
from ntserv.utils.cache import reload
from ntserv.utils.libserver import exc_req, home_page_text, self_route_rules

# Load SQL cache in-memory, if accessible
reload()

# Export the Sanic app
app = sanic.Sanic(__module__)
app.config.FORWARDED_SECRET = PROXY_SECRET

app.config.CORS_ORIGINS = ','.join(ALLOWED_ORIGINS)
Extend(app)


# TODO: blueprinting, e.g. /auth, /calc


# -------------------------
# Routes
# -------------------------
@app.route("/")
async def _(*args):
    _ = args
    return sanic.response.redirect("/api")


@app.route("/api")
async def _(*args):
    _ = args
    url_map = self_route_rules(app)
    home_page = home_page_text(url_map)
    return sanic.html(f"<pre>{home_page}</pre>", 200)


@app.route("/api/user_details")
async def _(request):
    return exc_req(get_user_details, request)


@app.route("/api/pg/version")
async def _(request):
    return exc_req(get_pg_version, request)


# ------------------------------------------------
# Public functions: /nutrients
# ------------------------------------------------
@app.route("/api/nutrients")
async def _(request):
    return exc_req(get_nutrients, request)


@app.route("/api/products")
async def _(request):
    return exc_req(get_nutrients, request)


@app.route("/api/nutrients/html")
async def _(request):
    return exc_req(get_nutrients, request, response_type="HTML")


# ------------------------------------------------
# Public functions: /calc
# ------------------------------------------------
@app.route("/api/calc/1rm", methods=["POST"])
async def _(request):
    return exc_req(post_calc_1rm, request)


@app.route("/api/calc/bmr", methods=["POST"])
async def _(request):
    return exc_req(post_calc_bmr, request)


@app.route("/api/calc/body-fat", methods=["POST"])
async def _(request):
    return exc_req(post_calc_body_fat, request)


@app.route("/api/calc/lbm-limits", methods=["POST"])
async def _(request):
    return exc_req(post_calc_lb_limits, request)


# -------------------------
# Account functions
# -------------------------
@app.route("/api/register", methods=["POST"])
async def _(request):
    return exc_req(post_register, request)


@app.route("/api/login", methods=["POST"])
async def _(request):
    return exc_req(post_login, request)


@app.route("/api/v2/login", methods=["POST"])
async def _(request):
    return exc_req(post_v2_login, request)


@app.route("/api/email/confirm")
async def _(request):
    return exc_req(get_confirm_email, request)


@app.route("/api/email/change")
async def _(request):
    return exc_req(get_email_change, request)


@app.route("/api/password/change")
async def _(request):
    return exc_req(get_password_change, request)


@app.route("/api/username/forgot", methods=["POST"])
async def _(request):
    return exc_req(post_username_forgot, request)


@app.route("/api/password/new/request")
async def _(request):
    return exc_req(post_password_new_request, request)


@app.route("/api/password/new/reset")
async def _(request):
    return exc_req(post_password_new_reset, request)


# ------------------------------------------------
# Sync functions
# ------------------------------------------------
@app.route("/api/sync", methods=["GET", "POST"])
async def _(request):
    return exc_req(opt_sync, request)
