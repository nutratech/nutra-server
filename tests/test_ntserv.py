# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 13:18:44 2020

@author: shane
"""
from datetime import datetime

import pytest

from ntserv.persistence.psql import verify_db_version_compat
from ntserv.routes import app
from ntserv.utils import release_git_parse


def test_verify_db_version_compat():
    assert verify_db_version_compat()


def test_release_git_parse():
    _release = release_git_parse()
    assert _release[0]
    assert datetime.strptime(_release[1], "%Y-%m-%d %H:%M:%S %z")


@pytest.mark.parametrize("gender", ["MALE", "FEMALE"])
def test_post_calc_bmr(gender: str):
    data = {
        "weight": 71,
        "height": 177,
        "gender": gender,
        "dob": 725864400,
        "bodyfat": 0.14,
        "activity_factor": 0.55,
    }
    _req, res = app.test_client.post("/calc/bmr", json=data)
    assert res.status_code == 200

    data = res.json["data"]
    if gender == "MALE":
        assert data == {
            "Katch-McArdle": [1689, 2618],
            "Cunningham": [1843, 2857],
            "Mifflin-St-Jeor": [1680, 2604],
            "Harris-Benedict": [1721, 2668],
        }
    else:
        assert data == {
            "Katch-McArdle": [1689, 2618],
            "Cunningham": [1843, 2857],
            "Mifflin-St-Jeor": [1514, 2347],
            "Harris-Benedict": [1525, 2363],
        }


def test_get_home_page():
    _req, res = app.test_client.get("/")
    assert 200 == res.status
