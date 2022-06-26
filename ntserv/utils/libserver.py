import time
import traceback
from datetime import datetime
from typing import Union

import sanic.response
from sanic import Sanic
from tabulate import tabulate

from ntserv import __email__, __release__, __url__, __version__
from ntserv.env import SERVER_HOST

# pylint: disable=invalid-name


def exc_req(func, req, response_type="JSON"):
    """Makes a request and handles global exceptions, always returning a `Response()`"""

    # TODO: do we want to use named arguments here?

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
# TODO: fix dict to accept either dict or list
def _response(
    err_msg: str = None, data: Union[dict, list] = None, code=-1
) -> sanic.HTTPResponse:
    """Creates a response object for the client"""

    if not data:
        data = {}

    if err_msg:
        data["error"] = err_msg  # type: ignore

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


# ------------------------------------------------
# Success paths
# ------------------------------------------------
def Success200Response(data: Union[dict, list] = None) -> sanic.HTTPResponse:
    return _response(data=data, code=200)


def MultiStatus207Response(data: dict = None) -> sanic.HTTPResponse:
    return _response(data=data, code=207)


# ------------------------------------------------
# Client errors
# ------------------------------------------------
def BadRequest400Response(err_msg="Bad request") -> sanic.HTTPResponse:
    return _response(err_msg=err_msg, code=400)


def Unauthenticated401Response(err_msg="Unauthenticated"):
    return _response(err_msg=err_msg, code=401)


def Forbidden403Response(err_msg="Forbidden") -> sanic.HTTPResponse:
    return _response(err_msg=err_msg, code=403)


# ------------------------------------------------
# Server errors
# ------------------------------------------------
def ServerError500Response(data: dict) -> sanic.HTTPResponse:
    # NOTE: injecting stacktrace for 500 is handled in the exc_req() method
    return _response(data=data, code=500)


def NotImplemented501Response(err_msg="Not Implemented") -> sanic.HTTPResponse:
    return _response(err_msg=err_msg, code=501)


# ------------------------
# Misc functions
# ------------------------
def home_page_text(routes_table: str):
    """Renders <pre></pre> compatible HTML home-page text"""

    # TODO: are any of these dynamic or environment based?
    email_link = f"<a href=mailto:{__email__}>{__email__}</a>"

    licsn_link = (
        '<a href="https://www.gnu.org/licenses" '
        'target="_blank">https://www.gnu.org/licenses</a>'
    )

    cli_link = (
        '<a href="https://pypi.org/project/nutra/" '
        'target="_blank">https://pypi.org/project/nutra/</a>'
    )

    src_link = f'<a href={__url__} target="blank">{__url__}</a>'

    prod_app = f"<a href={SERVER_HOST} " f'target="blank">{SERVER_HOST}</a>'

    # TODO: put UI_HOST link back... production server, production app, android app, etc

    return f"""
Welcome to nutra-server (v{__version__}) {__release__}
========================================================================

You can install our command line interface with Python and pip:

    pip3 install nutra


CLI page:          {cli_link}

Production server: {prod_app}

Source code:       {src_link}

------------------------------------------------------------------------
LICENSE & COPYING NOTICE
------------------------------------------------------------------------

    nutra-server, a tool for all things health, food, and fitness
    Copyright (C) 2019-2022  Shane Jaroch &lt{email_link}&gt

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
        if "GET" in methods:
            uri = f'<a href="{SERVER_HOST}{route.uri}">{route.uri}</a>'

        else:
            uri = route.uri
        rule = (" ".join(methods), uri)
        rules.append(rule)

    # Return string
    table = tabulate(rules, tablefmt="plain", headers=["methods", "route"])
    return table
