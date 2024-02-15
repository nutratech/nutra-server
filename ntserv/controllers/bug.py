#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 20:11:00 2024

@author: shane
"""
import sanic

import ntserv.utils.libserver as server


def post_bug_report(request: sanic.Request) -> sanic.HTTPResponse:
    """Stores user bug reports into our developer database"""
    # TODO: save in database, return 201 (or 204 if already there/duplicate submission)
    body = request.json
    return server.Response200Success(data=body)
