from ..postgres import psql

# ---------------
# Cache
# ---------------
users = {}
shipping_containers = {}
products = {}

nutrients = {}
nut_data = {}
food_des = {}
servings = {}
fdgrp = {}
data_src = {}


# ---------------
# Reload
# ---------------
def reload():
    global users, shipping_containers, products, nutrients, food_des, servings, fdgrp, data_src

    pg_result = psql("SELECT * FROM users()")
    users = {u["id"]: u for u in pg_result.rows}

    pg_result = psql("SELECT * FROM shipping_containers")
    shipping_containers = {c["id"]: c for c in pg_result.rows}

    pg_result = psql("SELECT * FROM products()")
    products = {x["id"]: x for x in pg_result.rows}

    pg_result = psql("SELECT * FROM nutrients()")
    nutrients = {n["id"]: n for n in pg_result.rows}

    pg_result = psql("SELECT * FROM food_des")
    food_des = {f["id"]: f for f in pg_result.rows}

    pg_result = psql("SELECT * FROM servings()")
    servings = {x["msre_id"]: x for x in pg_result.rows}
    servings_food = {x["food_id"]: x for x in pg_result.rows}

    pg_result = psql("SELECT * FROM fdgrp")
    fdgrp = {g["id"]: g for g in pg_result.rows}

    pg_result = psql("SELECT * FROM data_src")
    data_src = {d["id"]: d for d in pg_result.rows}
