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

These env vars can also be configured in a ``.env`` file
inside the ``sql`` folder.

A ``.env`` file is recommended in the ``server`` folder root as well.

**Option 1** point to HelioHost via PostgreSQL env vars:

.. code-block:: bash

    export PSQL_DATABASE=nutra_dev
    export PSQL_USER=nutra_admin
    export PSQL_PASSWORD=
    export PSQL_HOST=nutra.heliohost.org

**Option 2** create local db (see ``ntdb`` repo):

.. code-block:: bash

    export PSQL_LOCAL_DB_DIR="/home/$LOGNAME/.pgsql/nutra"
    mkdir -p $PSQL_LOCAL_DB_DIR

    git clone git@github.com:gamesguru/ntdb.git
    cd ntdb

    cd sql
    cp .env.local .env
    # exit the sql shell by entering \q
    bash local.sh
    bash rebuild.sh

Each time you reboot your computer, start the sql server:

.. code-block:: bash

    ./local.sh

Run (Local DB)
##############

.. code-block:: bash

    python3 server.py

You can also debug from VS Code.
Install the Python extension and press F5.

Run (Remote DB)
###############

TODO: this

Heroku Config (env) Variables
#############################

TODO: update

.. code-block:: bash

    JWT_SECRET         =
    ON_HEROKU          = 1
    ON_REMOTE          = 1
    PROD_EMAIL         = nutratracker@gmail.com
    PROD_EMAIL_PASS    =
    PSQL_DATABASE      = nutra
    PSQL_USER          = nutra
    PSQL_PASSWORD      =
    PSQL_HOST          = nutra.heliohost.org
