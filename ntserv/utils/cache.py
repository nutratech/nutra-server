from ..postgres import psql


# ---------------
# Cache
# ---------------
users = {}
shipping_containers = {}
variants = {}

nutr_def = {}
nut_data = {}
food_des = {}
fdgrp = {}
data_src = {}


# ---------------
# Reload
# ---------------
def reload():
    global users, shipping_containers, variants, nutr_def, nut_data, food_des, fdgrp, data_src

    pg_result = psql("SELECT id, passwd FROM users")
    users = {u["id"]: u for u in pg_result.rows}

    pg_result = psql("SELECT * FROM shipping_containers")
    shipping_containers = {c["id"]: c for c in pg_result.rows}

    pg_result = psql("SELECT * FROM variants")
    variants = {v["id"]: v for v in pg_result.rows}

    pg_result = psql("SELECT * FROM nutr_def")
    nutr_def = {n["id"]: n for n in pg_result.rows}

    pg_result = psql("SELECT * FROM nut_data")
    if pg_result.rows:
        for d in pg_result.rows:
            food_id = d["food_id"]
            id_val = (d["nutr_id"], d["nutr_val"])
            if food_id not in nut_data:
                nut_data[food_id] = [id_val]
            else:
                nut_data[food_id].append(id_val)
        # nut_data = {d["food_id"]: d for d in pg_result.rows}

    pg_result = psql("SELECT * FROM food_des")
    if pg_result.rows:
        food_des = {f["id"]: f for f in pg_result.rows}

    pg_result = psql("SELECT * FROM fdgrp")
    if pg_result.rows:
        fdgrp = {g["id"]: g for g in pg_result.rows}

    pg_result = psql("SELECT * FROM data_src")
    if pg_result.rows:
        data_src = {d["id"]: d for d in pg_result.rows}
