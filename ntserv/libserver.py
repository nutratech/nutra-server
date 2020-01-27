import json
import time
import traceback
from datetime import datetime

import requests

from .settings import SLACK_TOKEN


def Request(func, req):
    """ Makes a request and handles global exceptions, always returning a `Response()` """
    try:
        return func(request=req)
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
            "version": "0.0.1",
            "release": 1,
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
    """ Sends a slack alert message to simteam-extras channel """

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

    return f"""
Welcome to nutra-server, a open-sourced health and fitness app from Nutra, LLC.

Track obscure nutrients and stay healthy with Python and PostgreSQL!


Licensed under the GNU Public License, Version 3 (the "License");
you may not use this application except in accordance with the License.

    nutra-server, a server for nutratracker clients
    Copyright (C) 2020  Nutra, LLC. [Shane & Kyle] <nutratracker@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


Auto generated URL map:

{url_map}
"""


def self_route_rules(app):
    """ Gets human friendly url_map """

    rules = []

    for r in app.url_map._rules:
        methods = set(r.methods)
        # Remove unsightly ones
        for method in ["HEAD", "OPTIONS"]:
            try:
                methods.remove(method)
            except:
                pass
        # More filtering
        if str(r) != "/static/<path:filename>":
            rules.append(f"{str(methods).ljust(10)} {r}")

    # Return string
    return "\n".join(rules)
