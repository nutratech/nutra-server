from ..postgres import psql


# ---------------
# Cache
# ---------------
users = {}
shipping_containers = {}
variants = {}


# ---------------
# Reload
# ---------------
def reload():
    global users, shipping_containers, variants

    pg_result = psql("SELECT id, passwd FROM users")
    users = {u["id"]: u for u in pg_result.rows}

    pg_result = psql("SELECT * FROM shipping_containers")
    shipping_containers = {c["id"]: c for c in pg_result.rows}

    pg_result = psql("SELECT * FROM variants")
    variants = {v["id"]: v for v in pg_result.rows}


def get_shipping_containers():
    return shipping_containers


def get_variants():
    return variants
