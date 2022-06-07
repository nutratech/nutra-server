**************
 nutra-server
**************

.. image:: https://github.com/gamesguru/nutra-server/actions/workflows/test.yml/badge.svg
    :target: https://github.com/gamesguru/nutra-server/actions/workflows/test.yml
    :alt: Test status unknown|
.. image:: https://github.com/gamesguru/nutra-server/actions/workflows/lint.yml/badge.svg
    :target: https://github.com/gamesguru/nutra-server/actions/workflows/lint.yml
    :alt: Lint status unknown|
.. image:: https://badgen.net/badge/code%20style/black/000
    :target: https://github.com/ambv/black
    :alt: Code style: black|
.. image:: https://badgen.net/pypi/license/nutra
    :target: https://www.gnu.org/licenses/gpl-3.0.en.html
    :alt: License GPL-3

Backend server for ``nutra`` clients.

See database: https://github.com/gamesguru/ntdb

See cli: https://github.com/nutratech/cli

Dependencies
############

You will need to install the following, or newer.

- Python 3.7.0
- Postgres 12

Initialize Server
#################

Initialize with:

.. code-block:: bash

    make deps

Initialize Database
###################

**NOTE:** This is outdated.

These env vars can also be configured in a ``.env`` file inside the
``sql`` folder.


A ``.env`` file is recommended in the ``server`` folder root as well.

**Option 1** point to HelioHost (read-only instance) via PostgreSQL env vars:

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

Linting and Formatting
######################

The code is formatted with ``black``, ``autopep8``, and ``isort``.

You can format with ``make format``

The code is also linted with a variety of tools, see the ``Makefile``

You can lint with ``make lint``

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
