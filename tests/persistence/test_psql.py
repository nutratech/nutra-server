# -*- coding: utf-8 -*-
"""
Test cases for the Postgres module.
Created on Sat Feb  1 13:18:44 2020

@author: shane
"""
import pytest

from ntserv.persistence.psql import verify_db_version_compat


def test_verify_db_version_compat():
    """Verifies the version of the attached Postgres equals the target version"""
    try:
        assert verify_db_version_compat()
    except KeyError as err:
        print(f"WARN: {repr(err)}")
        pytest.skip("Skipping test... Postgres likely not running.")
