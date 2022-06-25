import time
import traceback
from datetime import datetime

import sanic.response
from sanic import Sanic
from tabulate import tabulate

from ntserv import __release__, __version__
from ntserv.env import SERVER_HOST


def exc_req(func, req, response_type="JSON"):
    """Makes a request and handles global exceptions, always returning a `Response()`"""

    try:
        # TODO: refactor services to accept unknown keywords, not crash on response_type
        if response_type == "JSON":
            return func(request=req)

        # else: HTML
        return func(request=req, response_type=response_type)

    # TODO: is this compatible with Sanic?
    # except BadRequestKeyError as err_bad_req:
    #     error_msg = f"{err_bad_req.name}: Missing arguments: {err_bad_req.args}"
    #     return BadRequest400Response(error_msg)

    # pylint: disable=broad-except
    except Exception as err_generic:
        return ServerError500Response(
            data={
                "error": "General server error",
                "exception": repr(err_generic),
                "stack": traceback.format_exc(),
            }
        )


# ------------------------
# Response types
# ------------------------
class Response(sanic.response.HTTPResponse):
    """Creates a response object for the client"""

    def __new__(  # type: ignore
        cls, err_msg: str = None, data: dict = None, code=-1
    ) -> sanic.response.HTTPResponse:

        if not data:
            data = {}

        if err_msg:
            data["error"] = err_msg

        return sanic.response.json(
            {
                "program": "nutra-server",
                "version": __version__,
                "release": __release__,
                "datetime": datetime.now().strftime("%c").strip(),
                "timestamp": round(time.time() * 1000),
                "ok": bool(code < 400),
                "code": code,
                "data": data,
            },
            status=code,
        )


class Success200Response(Response):
    def __new__(cls, message=None, data=None, code=200):
        return super().__new__(cls, message, data, code=code)


class MultiStatus207Response(Response):
    def __new__(cls, message=None, data=None, code=207):
        return super().__new__(cls, message, data, code=code)


class BadRequest400Response(Response):
    def __new__(cls, err_msg=None, code=408):
        return super().__new__(cls, data={"error": err_msg}, code=code)


class Unauthenticated401Response(Response):
    def __new__(cls, err_msg=None, code=401):
        return super().__new__(cls, data={"error": err_msg}, code=code)


class Forbidden403Response(Response):
    def __new__(cls, err_msg=None, code=403):
        return super().__new__(cls, data={"error": err_msg}, code=code)


class ServerError500Response(Response):
    def __new__(cls, data=None, code=500):
        # NOTE: injecting stacktrace for 500 is handled in the exc_req() method
        return super().__new__(cls, data=data, code=code)


class NotImplemented501Response(Response):
    def __new__(cls, err_msg="Not Implemented", code=501):
        return super().__new__(cls, err_msg=err_msg, code=code)


# ------------------------
# Helper functions
# ------------------------
def home_page_text(routes_table: str):
    """Renders <pre></pre> compatible HTML home-page text"""

    # TODO: are any of these dynamic or environment based?
    email_link = (
        '<a href="mailto:nutratracker@gmail.com" '
        'target="_blank" rel="noopener">nutratracker@gmail.com</a>'
    )

    licsn_link = (
        '<a href="https://www.gnu.org/licenses" '
        'target="_blank" >https://www.gnu.org/licenses</a>'
    )

    src_link = (
        "<a href=https://github.com/nutratech/nutra-server "
        'target="blank">https://github.com/nutratech/nutra-server</a>'
    )
    prod_app = f"<a href={SERVER_HOST} " f'target="blank">{SERVER_HOST}</a>'

    return f"""
Welcome to nutra-server (v{__version__}) {__release__}
========================================================================

An open-sourced health and fitness app from Nutra, LLC.
Track obscure nutrients and stay healthy with Python and PostgreSQL!

Source code:    &lt{src_link}&gt
Production app: &lt{prod_app}&gt

------------------------------------------------------------------------
LICENSE & COPYING NOTICE
------------------------------------------------------------------------

    nutra-server, a server for nutratracker clients
    Copyright (C) 2020  Nutra, LLC. [Shane & Kyle] &lt{email_link}&gt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see &lt{licsn_link}&gt

------------------------------------------------------------------------


URL map (auto-generated)
========================

{routes_table}
"""


def self_route_rules(app: Sanic) -> str:
    """Gets human friendly url_map"""

    routes = list(app.router.routes)
    routes.sort(key=lambda x: x.uri)

    rules = []

    for route in routes:
        methods = list(route.methods)
        methods.sort()

        # Remove default methods
        for method in ["HEAD", "OPTIONS"]:
            if method in methods:
                methods.remove(method)

        # TODO: examine this <path:filename> equivalent with Sanic
        # TODO: more extensive url map, e.g. route/query params, headers, body
        # Add to the list
        rule = (" ".join(methods), route.uri)
        rules.append(rule)

    # Return string
    table = tabulate(rules, headers=["methods", "route"])
    return table
