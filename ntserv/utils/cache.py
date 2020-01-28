from ..postgres import psql


# ---------------
# Cache
# ---------------
food_des = []
fdgrp = []


# ---------------
# Getters
# ---------------
# def food_des():
#     return _food_des


# def fdgrp():
#     return _fdgrp


# ---------------
# Reload
# ---------------
def reload():
    global food_des, fdgrp

    pg_result = psql("SELECT * FROM food_des")
    food_des = list(pg_result.rows)

    pg_result = psql("SELECT * FROM fdgrp")
    fdgrp = list(pg_result.rows)
