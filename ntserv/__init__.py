# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 16:01:31 2020

@author: shane

This file is part of nutra-server, a server for nutra clients.
    https://github.com/gamesguru/nutra-server

nutra-server is a server for nutra clients.
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

from ntserv.utils import heroku

PY_MIN_STR = "3.7.0"

__title__ = "nutra-server"
__version__ = "0.0.2"
__heroku__ = heroku()
__author__ = "gamesguru"
__email__ = "nutratracker@protonmail.com"
__license__ = "GPL v3"
__copyright__ = "Copyright 2019-2022 Shane Jaroch"
__url__ = "https://github.com/gamesguru/nutra-server"

__db_target_ntdb__ = "0.0.38"
