# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 13:18:44 2020

@author: shane
"""

from ntserv.postgres import verify_db_version_compat
from ntserv.server import get_home_page


def test_psql_version():
    assert verify_db_version_compat()


def test_root_url_returns_200():
    home_page = get_home_page()
    assert isinstance(home_page, str)
