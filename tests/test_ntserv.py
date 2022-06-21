# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 13:18:44 2020

@author: shane
"""
from datetime import datetime

import pytest
import sanic.response

from ntserv import release
from ntserv.postgres import verify_db_version_compat
from ntserv.server import get_home_page


def test_psql_version():
    assert verify_db_version_compat()


def test_release_git_parsing():
    _release = release()
    assert _release[0]
    assert datetime.strptime(_release[1], "%Y-%m-%d %H:%M:%S %z")


@pytest.mark.asyncio
async def test_root_url_returns_200():
    response = await get_home_page(request=None)

    assert isinstance(response, sanic.response.HTTPResponse)
    assert 200 == response.status
