# -*- coding: utf-8 -*-
"""
Created on Sun 26 Jun 2022 12:43:58 PM EDT

@author: shane
"""
from ntserv.routes import app


def test_get_home_page():
    _req, res = app.test_client.get("/")
    assert 200 == res.status


def test_post_calc_bmr():
    data = {
        "weight": 71,
        "height": 177,
        "gender": "MALE",
        "dob": 725864400,
        "bodyfat": 0.14,
        "activity_factor": 0.55,
    }
    _req, res = app.test_client.post("/calc/bmr", json=data)
    assert res.status_code == 200

    data = res.json["data"]
    assert data == {
        "Katch-McArdle": {"bmr": 1689, "tdee": 2618},
        "Cunningham": {"bmr": 1843, "tdee": 2857},
        "Mifflin-St-Jeor": {"bmr": 1680, "tdee": 2604},
        "Harris-Benedict": {"bmr": 1721, "tdee": 2668},
    }
