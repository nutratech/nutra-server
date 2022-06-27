# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 16:01:31 2020

@author: shane

This file is part of nutra-server, a server for nutra clients.
    https://github.com/gamesguru/nutra-server

nutra-server, a tool for all things health, food, and fitness
Copyright (C) 2019-2022  Shane Jaroch

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

import os

APP_HOME = os.path.dirname(os.path.realpath(__file__))

PY_MIN_STR = "3.7.0"

# ------------------------------------------------
# Package info
# ------------------------------------------------

__title__ = "nutra-server"
__module__ = "ntserv"
__version__ = "0.1.0.dev13"
__author__ = "Shane Jaroch"
__email__ = "chown_tee@proton.me"
__license__ = "GPL v3"
__copyright__ = "Copyright 2019-2022 Shane Jaroch"
__url__ = "https://github.com/nutratech/nutra-server"

# nt-sqlite database target version
__db_target_ntdb__ = "0.0.38"

# -------------------------------------------------
# Constants / configurations
# -------------------------------------------------
SEARCH_LIMIT = 100
CUSTOM_FOOD_DATA_SRC_ID = 6

NUTR_ID_KCAL = 208

NUTR_IDS_FLAVONES = [
    710,
    711,
    712,
    713,
    714,
    715,
    716,
    734,
    735,
    736,
    737,
    738,
    731,
    740,
    741,
    742,
    743,
    745,
    749,
    750,
    751,
    752,
    753,
    755,
    756,
    758,
    759,
    762,
    770,
    773,
    785,
    786,
    788,
    789,
    791,
    792,
    793,
    794,
]

NUTR_IDS_AMINOS = [
    501,
    502,
    503,
    504,
    505,
    506,
    507,
    508,
    509,
    510,
    511,
    512,
    513,
    514,
    515,
    516,
    517,
    518,
    521,
]
