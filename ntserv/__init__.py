# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 16:01:31 2020

@author: shane
"""
import os

try:
    from ntserv.__sha__ import COMMIT_DATE, COMMIT_SHA
except ImportError:
    print("Error reading git info, this is fine in development.")
    COMMIT_SHA = str()
    COMMIT_DATE = str()

APP_HOME = os.path.dirname(os.path.realpath(__file__))

PY_MIN_STR = "3.8.0"

# ------------------------------------------------
# Package info
# ------------------------------------------------

__title__ = "nutra-server"
__module__ = "ntserv"
__version__ = "0.1.0.dev17"
__release__ = " ".join([COMMIT_SHA, COMMIT_DATE]).strip() or None
__author__ = "Shane Jaroch"
__email__ = "chown_tee@proton.me"
__license__ = "GPL v3"
__copyright__ = "Copyright 2019-2022 Shane Jaroch"
__url__ = "https://github.com/nutratech/server"

# nt-sqlite database target version
__db_target_ntdb__ = "0.1.1.dev0"

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
