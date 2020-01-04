import stripe

from libserver.libserver import Response
from libserver.settings import STRIPE_API_KEY

# Set Stripe API key
stripe.api_key = STRIPE_API_KEY

# TODO - remove `result` attribute from: data={'result': products}


def GET_stripe_products(request):
    _products = stripe.Product
    products = []
    for p in _products.auto_paging_iter():
        if p['active']:
            products.append(p)

    return Response(data=products)


def GET_stripe_skus(request):
    _skus = stripe.SKU
    skus = []
    for s in _skus.auto_paging_iter():
        if s['active']:
            skus.append(s)

    return Response(data=skus)


def GET_products__product_id__reviews(request):
    product_id = request.view_args['id']
    return Response()


def POST_products_reviews(request):
    return Response()


def GET_products_avg_ratings(request):
    return Response()
