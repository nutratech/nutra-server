import stripe

from .libserver import Response
from .postgres import psql
from .settings import STRIPE_API_KEY

# Set Stripe API key
stripe.api_key = STRIPE_API_KEY

# TODO - remove `result` attribute from: data={'result': products}


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


def GET_products__product_id__reviews(request):

    product_id = request.view_args["id"]
    # product = stripe.Product.retrieve(product_id)

    pg_result = psql("SELECT * FROM reviews WHERE stripe_product_id=%s", [product_id])

    return Response(data=pg_result.rows)


def POST_products_reviews(request):
    return Response()


def GET_products_avg_ratings(request):

    pg_result = psql(
        "SELECT stripe_product_id, avg(rating) avg_rating FROM reviews GROUP BY stripe_product_id"
    )

    return Response(data=pg_result.rows)
