from ntserv.postgres import build_con, psql

# ---------------
# Cache
# ---------------
users = {}
shipping_containers = {}
products = {}
variants = {}

nutrients = {}
nut_data = {}
food_des = {}
servings = {}
servings_food = {}
fdgrp = {}
data_src = {}


# ---------------
# Reload
# ---------------
def reload():
    global users, shipping_containers, products, variants
    global nutrients, food_des, servings, servings_food, fdgrp, data_src

    con = build_con()
    if not con:
        print("WARN: skipping reload cache, can't build Postgres connection")
        return

    pg_result = psql("SELECT * FROM users()")
    users = {u["id"]: u for u in pg_result.rows}

    pg_result = psql("SELECT * FROM shipping_containers")
    shipping_containers = {c["id"]: c for c in pg_result.rows}

    pg_result = psql("SELECT * FROM products()")
    products = {x["id"]: x for x in pg_result.rows}

    pg_result = psql("SELECT * FROM variants")
    variants = {x["id"]: x for x in pg_result.rows}

    pg_result = psql("SELECT * FROM nutr_def")
    nutrients = {n["id"]: n for n in pg_result.rows}
