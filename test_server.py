# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 13:18:44 2020

@author: shane

This file is part of nutra, a nutrient analysis program.
    https://github.com/nutratech/cli
    https://pypi.org/project/nutra/

nutra-server, a server for nutratracker clients
Copyright (C) 2020  Nutra, LLC. [Shane & Kyle] mathmuncher11@gmail.com

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

import pytest
from fuzzywuzzy import fuzz

from ntserv.postgres import psql


@pytest.mark.skip(reason="work in progress, long running test")
def test_pair_foods():
    pg_result = psql("SELECT * FROM food_des")
    food_des = {f["id"]: f for f in pg_result.rows}

    keys = list(food_des.keys())
    scores = []
    for i in range(len(food_des)):
        print(f"food #: {i}")
        f1 = food_des[keys[i]]
        for j in range(i, len(food_des)):
            f2 = food_des[keys[j]]
            score = fuzz.token_set_ratio(f1["long_desc"], f2["long_desc"])
            scores.append(score)
    print(len(scores))
    # pg_result = psql("SELECT * FROM nut_data")

    # nut_data = {}
    # for row in pg_result.rows:
    #     food_id = row["food_id"]
    #     nutr_id = row["nutr_id"]
    #     nutr_val = row["nutr_val"]
    #     # Init food_id key
    #     if not food_id in nut_data:
    #         nut_data[food_id] = {}
    #     nut_data[food_id][nutr_id] = nutr_val

    # print(len(food_des))
    # print(len(nut_data))
