from ..postgres import psql


# ---------------
# Cache
# ---------------
users = []


# ---------------
# Reload
# ---------------
def reload():
    global users

    pg_result = psql("SELECT id, passwd FROM users")
    users = {u["id"]: u for u in pg_result.rows}
