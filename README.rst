**************
 nutra-server
**************

.. image:: https://api.travis-ci.com/gamesguru/nutra-server.svg?branch=master
    :target: https://travis-ci.com/gamesguru/nutra-server

Backend server for `nutra` clients.

See database: https://github.com/gamesguru/ntdb

Initialize Server
#################

Initialize with:

.. code-block:: bash

    pip3 install -r requirements.txt

Initialize Database
###################

These env vars can also be configured in a ``.env`` file inside the ``sql`` folder.

A ``.env`` file is recommended in the ``server`` folder root as well.

**Option 1** point to HelioHost via PostgreSQL env vars:

.. code-block:: bash

    export PSQL_DATABASE=nutra_dev
    export PSQL_USER=nutra_admin
    export PSQL_PASSWORD=
    export PSQL_HOST=nutra.heliohost.org

**Option 2** create local db (see ``nutra-db`` repo):

.. code-block:: bash

    export PSQL_LOCAL_DB_DIR="/home/$LOGNAME/postgres_nutra2_db"

    git clone git@github.com:gamesguru/ntdb.git
    cd nutra-db

    cd sql
    ./local.sh
    ./rebuild.sh

Run (Remote DB)
===============

TODO: this

Run (Local DB)
==============

You can also debug from VS Code.

.. code-block:: bash

    ./server.py

Heroku Config (env) Variables
#############################

.. code-block:: bash

    JWE_SECRET         = 
    ON_HEROKU          = 1
    PROD_EMAIL         = nutratracker@gmail.com
    PROD_EMAIL_PASS    = 
    PSQL_DATABASE      = nutra
    PSQL_USER          = nutra
    PSQL_PASSWORD      = 
    PSQL_HOST          = nutra.heliohost.org
