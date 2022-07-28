# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 16:30:30 2018

@author: shane
"""

import os

from setuptools import find_packages, setup

from ntserv import PY_MIN_STR, __author__, __email__, __title__, __version__

# cd to parent dir of setup.py
os.chdir(os.path.dirname(os.path.abspath(__file__)))

CLASSIFIERS = [
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Healthcare Industry",
    "Intended Audience :: Education",
    "Development Status :: 3 - Alpha",
    "Natural Language :: English",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Framework :: Flake8",
    "Framework :: Pytest",
    "Operating System :: OS Independent",
    "Operating System :: Microsoft :: Windows :: Windows XP",
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: SQL",
    "Programming Language :: Unix Shell",
]

with open("README.rst", encoding="utf-8") as file:
    README = file.read()

# NOTE: do we need to include requirements-*.txt in MANIFEST.in ?
with open("requirements.txt", encoding="utf-8") as file:
    REQUIREMENTS = file.read().split()

setup(
    name=__title__,
    author=__author__,
    author_email=__email__,
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
    python_requires=f">={PY_MIN_STR}",
    zip_safe=False,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    platforms=["linux", "darwin", "win32"],
    description="Server for our API and database",
    long_description=README,
    long_description_content_type="text/x-rst",
    url="https://github.com/gamesguru/nutra-server",
    license="GPL v3",
    version=__version__,
)
