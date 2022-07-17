********
 server
********

.. image:: https://github.com/gamesguru/nutra-server/actions/workflows/test.yml/badge.svg
    :target: https://github.com/gamesguru/nutra-server/actions/workflows/test.yml
    :alt: CI status: unknown
.. image:: https://github.com/nutratech/nutra-server/actions/workflows/deploy-dev.yml/badge.svg
    :target: https://github.com/nutratech/nutra-server/actions/workflows/deploy-dev.yml
    :alt: deploy-dev status: unknown
.. image:: https://github.com/nutratech/nutra-server/actions/workflows/deploy-prod.yml/badge.svg
    :target: https://github.com/nutratech/nutra-server/actions/workflows/deploy-prod.yml
    :alt: deploy-prod status: unknown
.. image:: https://badgen.net/badge/code%20style/black/000
    :target: https://github.com/ambv/black
    :alt: Code style: black
.. image:: https://badgen.net/pypi/license/nutra
    :target: https://www.gnu.org/licenses/gpl-3.0.en.html
    :alt: License: GPL-3

-------------------------------------------------------------------------------

Current URL: https://nutra.tk/api/

See database: https://github.com/nutratech/db

See cli: https://github.com/nutratech/cli

Dependencies
############

You will need to install the following, or newer.

- Python 3.7.0 (with ``venv`` support)
- PostgreSQL 12 (with ``dev`` library, see ``db`` for details)
- ``python3-dev`` for building ``Levenshtein/_levenshtein.c`` extension
  (optional)

Initialize Database
###################

You can install PostgreSQL, register it as a startup service,
and populate data.

You can also set the ``PSQL_*`` vars in ``.env`` and point to a
remote database instance.

See ``db/README.rst``.

Initialize Server
#################

Initialize with this.

It will require ``python-venv`` and (optionally) ``direnv``.

::

    make init
    make deps

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

The server runs with default configuration locally.

Check the ``.env.local`` file for specifics on deployed environments.

These can be supplied as environment variables to the ``systemctl`` service.
See ``ntserv.service`` for an example.
