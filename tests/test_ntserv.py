# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 13:18:44 2020

@author: shane
"""
import json
from datetime import datetime

import pytest
import sanic.response

from ntserv import release
from ntserv.postgres import verify_db_version_compat
from ntserv.server import app, get_home_page


def test_psql_version():
    assert verify_db_version_compat()


def test_release_git_parsing():
    _release = release()
    assert _release[0]
    assert datetime.strptime(_release[1], "%Y-%m-%d %H:%M:%S %z")


def test_bmr_calc():
    data = {
        "weight": 71,
        "height": 177,
        "gender": "MALE",
        "dob": 725864400,
        "bodyfat": 0.14,
        "activity_factor": 0.55,
    }
    _req, res = app.test_client.post("/calc/bmr", data=json.dumps(data))
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_root_url_returns_200():
    response = await get_home_page(request=None)

    assert isinstance(response, sanic.response.HTTPResponse)
    assert 200 == response.status
