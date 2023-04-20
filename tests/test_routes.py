# -*- coding: utf-8 -*-
"""
Test cases for routes.
Created on Sun 26 Jun 2022 12:43:58 PM EDT

@author: shane
"""
from ntserv.routes import app


def test_get_home_page():
    """Tests the home page route /"""
    _req, res = app.test_client.get("/")
    assert 200 == res.status


def test_post_calc_bmr():
    """Tests the calculate BMR endpoint"""
    data = {
        "weight": 71,
        "height": 177,
        "gender": "MALE",
        "dob": 725864400,
        "bodyFat": 0.14,
        "activityFactor": 0.55,
    }
    _req, res = app.test_client.post("/calc/bmr", json=data)
    assert res.status_code == 200
