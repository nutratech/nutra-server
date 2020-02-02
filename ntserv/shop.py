import jwt
import stripe

from .libserver import Response
from .postgres import psql
from .settings import JWT_SECRET, STRIPE_API_KEY
from .utils.account import user_id_from_username
from .utils.auth import AUTH_LEVEL_BASIC, auth

# Set Stripe API key
stripe.api_key = STRIPE_API_KEY

# TODO - remove `result` attribute from: data={'result': products}


def GET_products(request):
    pg_result = psql("SELECT * FROM get_products_ratings()")
    return Response(data=pg_result.rows)


def GET_skus(request):
    pg_result = psql("SELECT * FROM skus")
    return Response(data=pg_result.rows)


def GET_plans(request):
    pg_result = psql("SELECT * FROM plans")
    return Response(data=pg_result.rows)


def GET_stripe_products(request):
    _products = stripe.Product
    products = []
    for p in _products.auto_paging_iter():
        if p["active"]:
            products.append(p)

    return Response(data=products)


def GET_stripe_skus(request):
    _skus = stripe.SKU
    skus = []
    for s in _skus.auto_paging_iter():
        if s["active"]:
            skus.append(s)

    return Response(data=skus)


def GET_stripe_plans(request):
    _plans = stripe.Plan
    plans = []
    for p in _plans.auto_paging_iter():
        if p["active"]:
            plans.append(p)

    return Response(data=plans)


def GET_stripe_subscriptions(request):
    _subscriptions = stripe.Subscription
    subscriptions = []
    for s in _subscriptions.auto_paging_iter():
        if s["active"]:
            subscriptions.append(s)

    return Response(data=subscriptions)


@auth
def POST_orders(request, level=AUTH_LEVEL_BASIC, user_id=None):
    return Response(code=501)


@auth
def POST_products_reviews(request, level=AUTH_LEVEL_BASIC, user_id=None):

    # Parse incoming request
    body = request.json
    rating = body["rating"]
    review_text = body["review_text"]
    product_id = body["product_id"]

    #
    # Post review
    pg_result = psql(
        "INSERT INTO reviews (user_id, rating, review_text, product_id) VALUES (%s, %s, %s, %s) RETURNING id",
        [user_id, rating, review_text, product_id],
    )

    #
    # ERRORs
    if pg_result.err_msg:
        return pg_result.Response

    return Response(data=pg_result.rows)


def GET_products_avg_ratings(request):

    # TODO: deprecate, replace with /produces (it has average rating)
    pg_result = psql(
        "SELECT product_id, avg(rating)::REAL avg_rating FROM reviews GROUP BY product_id"
    )

    return Response(data=pg_result.rows)


def GET_products__product_id__reviews(request):

    # TODO: attach whole `pg_result` object, in case of generic errors. e.g. missing function?

    product_id = request.view_args["id"]
    pg_result = psql("SELECT * FROM get_product_reviews(%s)", [product_id])

    return Response(data=pg_result.rows)
