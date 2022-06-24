import traceback

import psycopg2

from ntserv.persistence.psql import build_con, psql
from ntserv.utils.logger import get_logger

_logger = get_logger(__name__)

# ---------------
# Cache
# ---------------
USERS = {}
SHIPPING_CONTAINERS = {}
PRODUCTS = {}
VARIANTS = {}

NUTRIENTS = {}


# nut_data = {}
# food_des = {}
# servings = {}
# servings_food = {}
# fdgrp = {}
# data_src = {}


def reload() -> bool:
    # pylint: disable=global-statement
    global USERS, SHIPPING_CONTAINERS, PRODUCTS, VARIANTS, NUTRIENTS
    # pylint: disable=global-statement
    # global food_des, servings, servings_food, fdgrp, data_src

    # Skip cache reloads if 1st connection attempt times out
    try:
        build_con()
    except psycopg2.OperationalError:
        _logger.warning("skipping reload cache, failed to build Postgres connection")
        _logger.warning(traceback.format_exc())
        return False

    # TODO: is this necessary with Postgres and Sanic running side-by-side? Any faster?
    # Reload cache
    pg_result = psql("SELECT * FROM users()")
    USERS = {u["id"]: u for u in pg_result.rows}

    pg_result = psql("SELECT * FROM shipping_containers")
    SHIPPING_CONTAINERS = {c["id"]: c for c in pg_result.rows}

    pg_result = psql("SELECT * FROM products()")
    PRODUCTS = {x["id"]: x for x in pg_result.rows}

    pg_result = psql("SELECT * FROM variants")
    VARIANTS = {x["id"]: x for x in pg_result.rows}

    pg_result = psql("SELECT * FROM nutr_def")
    NUTRIENTS = {n["id"]: n for n in pg_result.rows}

    return True
