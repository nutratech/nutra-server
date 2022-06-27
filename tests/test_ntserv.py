# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 13:18:44 2020

@author: shane
"""
from ntserv.persistence.psql import verify_db_version_compat


def test_verify_db_version_compat():
    assert verify_db_version_compat()
