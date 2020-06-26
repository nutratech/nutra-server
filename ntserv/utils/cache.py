from ..postgres import psql


# ---------------
# Cache
# ---------------
users = {}
shipping_containers = {}
variants = {}

nut_data = {}
food_des = {}
fdgrp = {}
data_src = {}


# ---------------
# Reload
# ---------------
def reload():
    global users, shipping_containers, variants, nut_data, food_des, fdgrp, data_src

    pg_result = psql("SELECT id, passwd FROM users")
    users = {u["id"]: u for u in pg_result.rows}

    pg_result = psql("SELECT * FROM shipping_containers")
    shipping_containers = {c["id"]: c for c in pg_result.rows}

    pg_result = psql("SELECT * FROM variants")
    variants = {v["id"]: v for v in pg_result.rows}

    # pg_result = psql("SELECT * FROM usda.nut_data")
    # nut_data = {}

    pg_result = psql("SELECT * FROM usda.food_des")
    food_des = {f["id"]: f for f in pg_result.rows}

    pg_result = psql("SELECT * FROM usda.fdgrp")
    fdgrp = {g["id"]: g for g in pg_result.rows}

    pg_result = psql("SELECT * FROM usda.data_src")
    data_src = {d["id"]: d for d in pg_result.rows}
