import stripe

from ..postgres import psql
from ..settings import STRIPE_API_KEY

# Set Stripe API key
stripe.api_key = STRIPE_API_KEY

# ---------------
# Cache
# ---------------
food_des = []
fdgrp = []
users = []
customers = []


# ---------------
# Reload
# ---------------
def reload():
    global food_des, fdgrp, users, customers

    pg_result = psql("SELECT * FROM food_des")
    food_des = {f["id"]: f for f in pg_result.rows}

    pg_result = psql("SELECT * FROM fdgrp")
    fdgrp = {g["id"]: g for g in pg_result.rows}

    pg_result = psql("SELECT id, passwd FROM users")
    users = {u["id"]: u for u in pg_result.rows}

    customers = {c.email: c for c in stripe.Customer.auto_paging_iter()}
