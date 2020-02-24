from ..postgres import psql


# ---------------
# Cache
# ---------------
nut_data = []
food_des = []
fdgrp = []
data_src = []
users = []


# ---------------
# Reload
# ---------------
def reload():
    global food_des, fdgrp, data_src, users

    # pg_result = psql("SELECT * FROM nut_data")
    # nut_data = {}

    pg_result = psql("SELECT * FROM food_des")
    food_des = {f["id"]: f for f in pg_result.rows}

    pg_result = psql("SELECT * FROM fdgrp")
    fdgrp = {g["id"]: g for g in pg_result.rows}

    pg_result = psql("SELECT * FROM data_src")
    data_src = {d["id"]: d for d in pg_result.rows}

    pg_result = psql("SELECT id, passwd FROM users")
    users = {u["id"]: u for u in pg_result.rows}
