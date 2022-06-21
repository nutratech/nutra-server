**************
 nutra-server
**************

.. image:: https://github.com/gamesguru/nutra-server/actions/workflows/test.yml/badge.svg
    :target: https://github.com/gamesguru/nutra-server/actions/workflows/test.yml
    :alt: Test status unknown|
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

- Python 3.7.0 (with ``venv`` support)
- PostgreSQL 12 (with ``dev`` library)

Initialize Server
#################

Initialize with this.

::

    make init
    make deps

Initialize Database
###################

See ``ntdb/README.rst``.

You can install Postgres, register it as a startup service, and populate data.

Run
###

::

    make run

**NOTE:** You can also debug from VS Code, or PyCharm.

**NOTE:** You can also set the ``PSQL_*`` vars in ``.env`` and point to a
remote database instance.

Lint, Test, and Format
######################

The code is formatted with ``black``, ``autopep8``, and ``isort``.

You can format with this.

::

    make format

The code is also linted with a variety of tools, see the ``Makefile``

You can lint with this.

::

    make lint

The code is tested with ``pytest`` and ``coverage``.

The unit tests require a Postgres connection. Run them like this.

::

    make test

Config Variables in ``.env`` file
#################################

**TODO:** update this to the latest.

.. code-block:: bash

    JWT_SECRET         = secret
    ON_REMOTE          = 1
    PROD_EMAIL         =
    PROD_EMAIL_PASS    =
    PSQL_DATABASE      = nt
    PSQL_USER          = $LOGNAME
    PSQL_PASSWORD      = password
    PSQL_HOST          = localhost
