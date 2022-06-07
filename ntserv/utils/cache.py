from ntserv.postgres import build_con, psql

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


def reload() -> None:
    # pylint: disable=global-statement
    global USERS, SHIPPING_CONTAINERS, PRODUCTS, VARIANTS, NUTRIENTS
    # pylint: disable=global-statement
    # global food_des, servings, servings_food, fdgrp, data_src

    con = build_con()
    if not con:
        print("WARN: skipping reload cache, can't build Postgres connection")
        return

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
