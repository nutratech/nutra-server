import jwt
import stripe

from .libserver import Response
from .postgres import psql
from .settings import JWT_SECRET, STRIPE_API_KEY
from .utils.account import user_id_from_username

# Set Stripe API key
stripe.api_key = STRIPE_API_KEY

# TODO - remove `result` attribute from: data={'result': products}


def GET_products(request):
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


def POST_products_reviews(request):

    # Parse incoming request
    body = request.json
    rating = body["rating"]
    review_text = body["review_text"]
    try:
        product_id = body["product_id"]
    except:
        # TODO: deprecate
        product_id = body["stripe_product_id"]

    token = jwt.decode(request.headers["authorization"].split()[1], JWT_SECRET)

    # Get user_id
    user_id = user_id_from_username(token["username"])

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

    pg_result = psql(
        "SELECT product_id, avg(rating)::float avg_rating FROM reviews GROUP BY product_id"
    )

    return Response(data=pg_result.rows)


def GET_products__product_id__reviews(request):

    # TODO: attach whole `pg_result` object, in case of generic errors. e.g. missing function?

    product_id = request.view_args["id"]
    pg_result = psql("SELECT * FROM get_product_reviews(%s)", [product_id])

    return Response(data=pg_result.rows)
