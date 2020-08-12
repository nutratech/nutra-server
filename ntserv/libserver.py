import json
import time
import traceback
from datetime import datetime

import requests

from . import __heroku__, __version__
from .settings import SLACK_TOKEN


def Request(func, req, response_type="JSON"):
    """ Makes a request and handles global exceptions, always returning a `Response()` """
    try:
        if response_type == "JSON":
            return func(request=req)
        else:  # HTML
            return func(request=req, response_type=response_type)
    except Exception as e:
        # Prepare error messages
        trace = "\n".join(traceback.format_tb(e.__traceback__))
        stack_msg = f"{repr(e)}\n\n{trace}"
        request = json.dumps(req.__dict__, default=lambda o: "<not serializable>")
        # Slack msg
        slack_msg(f"Application Error\n\n{request}\n\n{stack_msg}")
        return Response(
            data={"error": "General server error", "stack": stack_msg}, code=500
        )


def Response(data={}, code=200, status="OK"):
    """ Creates a response object for the client """

    return (
        {
            "program": "nutra-server",
            "version": __version__,
            "release": int(__heroku__[0][1:]) if __heroku__[0] else __heroku__[0],
            "datetime": datetime.now().strftime("%c").strip(),
            "timestamp": int(time.time() * 1000),
            "status": status if code < 400 else "Failure",
            "code": code,
            "data": data,
        },
        code,
    )


def Text(text=None):
    return text


"""
------------------------
Helper functions
------------------------
"""


def slack_msg(msg):
    """ Sends a slack alert message to nutra1 prod-alerts channel """

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
        "https://slack.com/api/chat.postMessage", headers=headers, json=body,
    )


def home_page_text(url_map):
    """ Renders <pre></pre> compatible HTML home-page text """

    email_link = f'<a href="mailto:nutratracker@gmail.com" target="_blank" rel="noopener">nutratracker@gmail.com</a>'
    licsn_link = f'<a href="https://www.gnu.org/licenses" target="_blank" >https://www.gnu.org/licenses</a>'
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
    """ Gets human friendly url_map """

    rules = []

    map_rules = app.url_map._rules
    map_rules.sort(key=lambda x: x.rule)

    for r in map_rules:
        methods = set(r.methods)
        # Remove unsightly ones
        for method in ["HEAD", "OPTIONS"]:
            if method in methods:
                methods.remove(method)
        # More filtering
        if str(r) != "/static/<path:filename>":
            rule = r.rule.replace("<", "&lt").replace(">", "&gt")
            rules.append(f"{str(methods).ljust(30)} {rule}")

    # Return string
    return "\n".join(rules)
