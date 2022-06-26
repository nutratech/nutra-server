# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 13:18:44 2020

@author: shane
"""
from datetime import datetime

from ntserv.persistence.psql import verify_db_version_compat
from ntserv.utils import release_git_parse


def test_verify_db_version_compat():
    assert verify_db_version_compat()


def test_release_git_parse():
    _release = release_git_parse()
    assert _release[0]
    assert datetime.strptime(_release[1], "%Y-%m-%d %H:%M:%S %z")
