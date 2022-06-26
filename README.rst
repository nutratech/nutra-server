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

-------------------------------------------------------------------------------

Current URL: https://vps76.heliohost.us/

See database: https://github.com/gamesguru/ntdb

See cli: https://github.com/nutratech/cli

Dependencies
############

You will need to install the following, or newer.

- Python 3.7.0 (with ``venv`` support)
- PostgreSQL 12 (with ``dev`` library, see ``ntdb`` for details)

Initialize Server
#################

Initialize with this.

It will require ``python-venv`` and (optionally) ``direnv``.

::

    make init
    make deps

Initialize Database
###################

You can install Postgres, register it as a startup service, and populate data.

You can also set the ``PSQL_*`` vars in ``.env`` and point to a
remote database instance.

See ``ntdb/README.rst``.

Run
###

::

    make run

**NOTE:** You can also debug from ``VSCode``, or ``PyCharm``.

Format, Lint, and Test
######################

The code is formatted with ``black``, ``autopep8``, and ``isort``.
The code is also linted with a variety of tools, see the ``Makefile``

The code is tested with ``pytest`` and ``coverage``.
The unit tests require a Postgres connection.
They use the recommended practices for testing a ``Sanic`` app.

**NOTE:** It's recommended to run this before committing changes.

::

    make format lint test

Config Variables in ``.env`` file
#################################

**TODO:** Check which are required, and which will be overwritten as ``null``.

.. code-block:: ini

    # Email creds
    PROD_EMAIL=
    PROD_EMAIL_PASS=

    # Remote PostgreSQL
    # PSQL_USER=
    # PSQL_PASSWORD=
    # PSQL_DB_NAME=
    # PSQL_HOST=

    # Server host
    # HOST=127.0.0.1

    # Other
    # JWT_SECRET=
    # PROXY_SECRET=

    # ENV=prod
    # WORKERS=4
