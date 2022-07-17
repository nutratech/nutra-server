# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 13:18:44 2020

@author: shane
"""
import pytest

from ntserv.persistence.psql import verify_db_version_compat


def test_verify_db_version_compat():
    try:
        assert verify_db_version_compat()
    except KeyError:
        pytest.skip("Skipping test... Postgres likely not running.")
