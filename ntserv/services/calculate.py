#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 20:53:14 2020

@author: shane

This file is part of nutra-server, a server for nutra clients.
    https://github.com/gamesguru/nutra-server

nutra-server is a server for nutra clients.
Copyright (C) 2019-2020  Shane Jaroch

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
"""

from datetime import datetime

# TODO: generalize activity level across BMR calcs, e.g. LIGHT, MODERATE, EXTREME


def _age(dob):
    now = datetime.now().timestamp()
    years = (now - dob) / (365 * 24 * 3600)
    return years


def bmr_katch_mcardle(lbm, activity_factor):
    bmr = 370 + (21.6 * lbm)
    tdee = bmr * (1 + activity_factor)
    return round(bmr), round(tdee)


def bmr_cunningham(lbm, activity_factor):
    bmr = 500 + 22 * lbm
    tdee = bmr * (1 + activity_factor)
    return round(bmr), round(tdee)


def bmr_mifflin_st_jeor(gender, weight, height, dob, activity_factor):
    _bmr = 10 * weight + 6.25 + 6.25 * height - 5 * _age(dob)
    if gender == "MALE":
        bmr = _bmr + 5
    elif gender == "FEMALE":
        bmr = _bmr - 161

    tdee = bmr * (1 + activity_factor)
    return round(bmr), round(tdee)


def bmr_harris_benedict(gender, weight, height, dob, activity_factor):
    age = _age(dob)

    if gender == "MALE":
        bmr = (13.397 * weight + 4.799 * height - 5.677 * age) + 88.362
    elif gender == "FEMALE":
        bmr = (9.247 * weight + 3.098 * height - 4.330 * age) + 447.593

    tdee = bmr * (1 + activity_factor)
    return round(bmr), round(tdee)
