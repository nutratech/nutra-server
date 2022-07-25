"""Dumping grounds for things related to URL routes, responses and  the home page"""
import time
import traceback
from datetime import datetime
from typing import Callable, Union

import sanic.response
from sanic import Sanic
from tabulate import tabulate

from ntserv import __email__, __release__, __title__, __url__, __version__
from ntserv.env import (
    BLOG_HOST,
    SERVER_HOST,
    SERVER_HOST_BASE,
    SERVER_HOST_DEV,
    SERVER_HOST_PROD,
    UI_HOST,
)

# pylint: disable=invalid-name


def exc_req(
    func: Callable[..., sanic.HTTPResponse],
    req: sanic.Request,
    response_type: str = "JSON",
) -> sanic.HTTPResponse:
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
        return Response500ServerError(
            data={
                "errMsg": f"General server error — {repr(err_generic)}",
                "stack": traceback.format_exc(),
            }
        )


# ------------------------
# Response types
# ------------------------
# TODO: fix dict to accept either dict or list
def _response(
    err_msg: str = str(),
    stack: str = str(),
    data: Union[dict, list] = None,
    code: int = -1,
) -> sanic.HTTPResponse:
    """Creates a response object for the client"""

    if not data:
        data = {}

    # TODO: separate methods for data as dict, vs. data as list
    if err_msg:
        data["errMsg"] = err_msg  # type: ignore
    if stack:
        data["stack"] = stack  # type: ignore

    # TODO: standardize validation / stack / other errMsg info
    #  Ideally we should have a danger alter pop in the UI, or similar with the format:
    #  errHeader: errMsg/errDescription

    return sanic.response.json(
        {
            "program": __title__,
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
# noinspection PyPep8Naming
def Response200Success(data: Union[dict, list] = None) -> sanic.HTTPResponse:
    """200 response"""
    return _response(data=data, code=200)


# noinspection PyPep8Naming
def Response207MultiStatus(data: dict = None) -> sanic.HTTPResponse:
    """207 response"""
    return _response(data=data, code=207)


# ------------------------------------------------
# Client errors
# ------------------------------------------------
# noinspection PyPep8Naming
def Response400BadRequest(
    err_msg: str = "Bad request", stack: str = str()
) -> sanic.HTTPResponse:
    """400 response"""
    return _response(err_msg=err_msg, stack=stack, code=400)


# noinspection PyPep8Naming
def Response401Unauthenticated(err_msg: str = "Unauthenticated") -> sanic.HTTPResponse:
    """401 response"""
    return _response(err_msg=err_msg, code=401)


# TODO: use this instead of 401 for some cases?
# noinspection PyPep8Naming
def Response403Forbidden(err_msg: str = "Forbidden") -> sanic.HTTPResponse:
    """403 response"""
    return _response(err_msg=err_msg, code=403)


# ------------------------------------------------
# Server errors
# ------------------------------------------------
# noinspection PyPep8Naming
def Response500ServerError(data: dict) -> sanic.HTTPResponse:
    """
    500 response
    This is a generic catchall, which will typically include a stack and errMsg
    """
    # NOTE: injecting stacktrace for 500 is handled in the exc_req() method
    return _response(data=data, code=500)


# noinspection PyPep8Naming
def Response501NotImplemented(err_msg: str = "Not Implemented") -> sanic.HTTPResponse:
    """501 response"""
    return _response(err_msg=err_msg, code=501)


# ------------------------
# Misc functions
# ------------------------
def a_href(link: str, target: str = str()) -> str:
    """Creates an HREF link"""
    if target:
        return f'<a href="{link}" target="{target}">{link}</a>'
    return f'<a href="{link}">{link}</a>'


def home_page_text(routes_table: str) -> str:
    """Renders <pre></pre> compatible HTML home-page text"""

    # TODO: are any of these dynamic or environment based?
    email_link = f"<a href=mailto:{__email__}>{__email__}</a>"

    license_link = a_href("https://www.gnu.org/licenses", target="_blank")

    cli_link = a_href("https://pypi.org/project/nutra/", target="_blank")

    src_link = a_href(__url__)

    server_prod = a_href(SERVER_HOST_PROD)

    server_dev = a_href(SERVER_HOST_DEV)

    website_link = a_href(UI_HOST, target="blank")
    server_link = a_href(SERVER_HOST)
    blog_link = a_href(BLOG_HOST, target="blank")

    # TODO: put UI_HOST link back... production server, production app, android app, etc

    return f"""
Welcome to nutra-server (v{__version__}) [{__release__}]
========================================================================

You can install our command line interface with Python and pip.

    pip3 install nutra


Website:              {website_link}

API server:           {server_link}

Blog:                 {blog_link}



Production server:    {server_prod}

Dev server:           {server_dev}



Server Source code:   {src_link}

CLI page:             {cli_link}


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
    along with this program.  If not, see &lt{license_link}&gt

------------------------------------------------------------------------


URL map (auto-generated)
========================

{routes_table}
"""


def self_route_rules(app: Sanic) -> str:
    """Gets human friendly url_map"""

    routes = list(app.router.routes)
    routes.sort(key=lambda x: x.uri)  # type: ignore

    rules = []

    for route in routes:
        methods = list(route.methods)
        methods.sort()

        # Skip default methods
        _method = next(iter(methods), None)
        if _method in {"HEAD", "OPTIONS"}:
            continue

        # TODO: examine this <path:filename> equivalent with Sanic
        # TODO: more extensive url map, e.g. route/query params, headers, body
        # Add to the list
        if "GET" in methods:
            uri = f'<a href="{SERVER_HOST_BASE}{route.uri}">{route.uri}</a>'
        else:
            uri = route.uri

        rule = (" ".join(methods), uri)
        rules.append(rule)

    # Return string
    table = tabulate(rules, tablefmt="plain", headers=["methods", "route"])
    return table
