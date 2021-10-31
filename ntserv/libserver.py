import json
import time
import traceback
from datetime import datetime

import requests
from tabulate import tabulate
from werkzeug.exceptions import BadRequestKeyError

from . import __heroku__, __version__
from .settings import SLACK_TOKEN


def Request(func, req, response_type="JSON"):
    """Makes a request and handles global exceptions, always returning a `Response()`"""

    try:
        if response_type == "JSON":
            return func(request=req)
        else:  # HTML
            return func(request=req, response_type=response_type)

    except BadRequestKeyError as e:
        error_msg = f"{e.name}: Missing arguments: {e.args}"
        return BadRequest400Response(error_msg)

    except Exception as e:
        return ServerError500Response(e, req)


class Response:
    def __new__(self, message=None, data={}, code=200):
        """Creates a response object for the client"""

        if message:
            data["message"] = message

        return (
            {
                "program": "nutra-server",
                "version": __version__,
                "release": int(__heroku__[0][1:]) if __heroku__[0] else __heroku__[0],
                "datetime": datetime.now().strftime("%c").strip(),
                "timestamp": round(time.time() * 1000),
                "status": "OK" if code < 400 else "Failure",
                "code": code,
                "data": data,
            },
            code,
        )


class Success200Response(Response):
    def __new__(self, message=None, data={}):
        return super().__new__(self, message, data)


class MultiStatus207Response(Response):
    def __new__(self, message=None, data={}):
        return super().__new__(self, message, data, code=207)


class BadRequest400Response(Response):
    def __new__(self, error_msg):
        return super().__new__(self, data={"error": error_msg}, code=400)


class Unauthenticated401Response(Response):
    def __new__(self, error_msg):
        return super().__new__(self, data={"error": error_msg}, code=401)


class Forbidden403Response(Response):
    def __new__(self, error_msg):
        return super().__new__(self, data={"error": error_msg}, code=403)


class ServerError500Response(Response):
    def __new__(self, exception, request):
        # trace = self.friendly_stack(self, exception)
        # TODO: rethink slack workflow
        # self.dispatch_slack_msg(self, request, trace)
        return super().__new__(
            # TODO: rethink structure of 500 response? include exception type?
            self,
            data={
                "error": "General server error",
                "exception": repr(exception),
                # "stack": None,
            },
            code=500,
        )

    def friendly_stack(self, exception):
        trace = "\n".join(traceback.format_tb(exception.__traceback__))
        return repr(exception) + "\n\n" + trace

    def dispatch_slack_msg(self, req, trace):
        request = json.dumps(req.__dict__, default=lambda o: "<not serializable>")
        slack_msg(f"Application Error\n\n{request}\n\n{trace}")


class NotImplemented501Response(Response):
    def __new__(self, message="Not implemented", data={}):
        return super().__new__(self, message, data, code=501)


def Text(text=None):
    return text


"""
------------------------
Helper functions
------------------------
"""


def slack_msg(msg):
    """Sends a slack alert message to nutra1 prod-alerts channel"""

    # Print
    print(msg)

    # Prep body && headers
    body = {
        "channel": "CSBL81C4F",
        "username": "ntserv",
        "text": f"```{msg}```",
        "icon_url": "https://www.nutritionix.com/nix_assets/images/nix_apple.png",
    }

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {SLACK_TOKEN}",
    }

    # Make post
    requests.post(
        "https://slack.com/api/chat.postMessage",
        headers=headers,
        json=body,
    )


def home_page_text(url_map):
    """Renders <pre></pre> compatible HTML home-page text"""

    email_link = '<a href="mailto:nutratracker@gmail.com" target="_blank" rel="noopener">nutratracker@gmail.com</a>'
    licsn_link = '<a href="https://www.gnu.org/licenses" target="_blank" >https://www.gnu.org/licenses</a>'
    return f"""
Welcome to nutra-server (v{__version__})
heroku {__heroku__[0]}, commit {__heroku__[1]} [{__heroku__[2]}]
=======================================================

An open-sourced health and fitness app from Nutra, LLC.
Track obscure nutrients and stay healthy with Python and PostgreSQL!

Source code:    &lt<a href=https://github.com/gamesguru/nutra-server target="blank">https://github.com/gamesguru/nutra-server</a>&gt
Production app: &lt<a href=https://nutra-web.herokuapp.com target="blank">https://nutra-web.herokuapp.com</a>&gt

--------------------------------------------------------------------
LICENSE & COPYING NOTICE
--------------------------------------------------------------------

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

--------------------------------------------------------------------


URL map (auto-generated)
========================

{url_map}
"""


def self_route_rules(app):
    """Gets human friendly url_map"""

    map_rules = app.url_map._rules
    map_rules.sort(key=lambda x: x.rule)

    rules = []

    for r in map_rules:
        methods = set(r.methods)

        # Remove default methods
        for method in ["HEAD", "OPTIONS"]:
            if method in methods:
                methods.remove(method)

        # More filtering
        if str(r) != "/static/<path:filename>":
            rule = r.rule.replace("<", "&lt").replace(">", "&gt")
            rule = (str(methods), rule)
            rules.append(rule)

    # Return string
    table = tabulate(rules, headers=["methods", "route"])
    return table
