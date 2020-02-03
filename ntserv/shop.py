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


def GET_countries(request):
    pg_result = psql("SELECT * FROM get_countries_states()")
    return Response(data=pg_result.rows)


def GET_shipping_methods(request):
    pg_result = psql("SELECT * FROM shipping_methods")
    return Response(data=pg_result.rows)


def GET_products_ratings(request):
    pg_result = psql("SELECT * FROM get_products_ratings()")
    return Response(data=pg_result.rows)


def GET_products_variants(request):
    pg_result = psql("SELECT * FROM get_products_variants()")
    return Response(data=pg_result.rows)


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


def GET_products__product_id__reviews(request):

    # TODO: attach whole `pg_result` object, in case of generic errors. e.g. missing function?

    product_id = request.view_args["id"]
    pg_result = psql("SELECT * FROM get_product_reviews(%s)", [product_id])

    return Response(data=pg_result.rows)
