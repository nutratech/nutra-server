nutra-server
------------

.. image:: https://api.travis-ci.com/gamesguru/nutra-server.svg?branch=master
    :target: https://travis-ci.com/gamesguru/nutra-server

Backend server for `nutra` clients.

Initialize Server
=================

Initialize with:

.. code-block:: bash

    git submodule update --init --recursive
    pip3 install -r requirements.txt
    cd db
    pip3 install -r requirements.txt
    cd ..
    ./local.cmd

Initialize Database
===================

**Option 1** point to AWS via PostgreSQL env vars:

.. code-block:: bash

    export PSQL_DATABASE=nutra2
    export PSQL_USER=nutra
    export PSQL_PASSWORD=<NOPE>
    export PSQL_HOST=<NOPE>

**Option 2** create local db (see ``nutra-db`` repo):

.. code-block:: bash

    export PSQL_LOCAL_DB_DIR="/home/$LOGNAME/postgres_nutra2_db"

    git clone git@github.com:gamesguru/nutra-db.git
    cd nutra-db

    cd sql
    ./local.cmd
    \i startup.sql

Run (Remote DB)
===============

Running the server is simple:

.. code-block:: bash

    ./server.py

Run (Local DB)
==============

The ``local.cmd`` script unsets environment variables telling the server to point to the remote database:

.. code-block:: bash

    ./local.cmd

Heroku Config (env) Variables
=============================


.. code-block:: bash

    JWE_SECRET         = <NOPE>
    ON_HEROKU          = 1
    PROD_EMAIL         = nutratracker@gmail.com
    PROD_EMAIL_PASS    = <NOPE>
    PSQL_DATABASE      = nutra2
    PSQL_USER          = nutra
    PSQL_PASSWORD      = <NOPE>
    PSQL_HOST          = <NOPE>
