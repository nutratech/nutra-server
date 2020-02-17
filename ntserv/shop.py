import re

import jwt
import shippo
import stripe
from py3dbp.main import Bin, Item, Packer

from .libserver import Response
from .postgres import psql
from .settings import JWT_SECRET, SHIPPO_API_KEY, STRIPE_API_KEY
from .utils.account import user_id_from_username
from .utils.auth import AUTH_LEVEL_BASIC, auth

# Set Stripe & Shippo API keys
shippo.config.api_key = SHIPPO_API_KEY
stripe.api_key = STRIPE_API_KEY

address_from = {
    "street1": "100 Renaissance Center",
    "street2": "Ste 1014",
    "city": "Detroit",
    "state": "MI",
    "zip": 48243,
    "country": "US",
}


def GET_countries(request):
    pg_result = psql("SELECT * FROM get_countries_states()")
    return Response(data=pg_result.rows)


def POST_shipping_esimates(request):
    body = request.json
    address = body["address"]
    items = body["items"]

    # Query DB for products, shipping methods and containers
    pg_result = psql("SELECT * FROM variants")
    variants = {r["id"]: r for r in pg_result.rows}
    # TODO - reduce down to subset of shipping options (more user-friendly?)
    # pg_result = psql("SELECT * FROM shipping_methods WHERE is_physical=TRUE")
    # methods = pg_result.rows
    pg_result = psql("SELECT * FROM shipping_containers")
    containers = pg_result.rows

    #############
    # 3D bin-pack
    packer = Packer()

    for c in containers:
        l = c["dimensions"][0]
        w = c["dimensions"][1]
        h = c["dimensions"][2]
        bin = Bin(c["tag"], l, w, h, c["weight_max"])
        packer.add_bin(bin)

    for i in items:
        # TODO - include stock/inventory check at this point, or earlier in shop
        i = variants[i]
        l = i["dimensions"][0] / 2.54
        w = i["dimensions"][1] / 2.54
        h = i["dimensions"][2] / 2.54
        weight = i["weight"]
        item = Item(i["denomination"], l, w, h, weight)
        packer.add_item(item)

    packer.pack()

    bins = [bin for bin in packer.bins if bin.items]

    ########
    # SHIPPO
    parcels = []
    for bin in bins:
        parcel = {
            "length": bin.width,
            "width": bin.height,
            "height": bin.depth,
            "distance_unit": "in",
            "weight": sum([i.weight for i in bin.items]),
            "mass_unit": "g",
        }
        parcels.append(parcel)

    shipment = shippo.Shipment.create(
        address_from=address_from,
        address_to=address,
        parcels=parcels,
        asynchronous=False,
    )

    return Response(data={"bins": bins, "rates": shipment.rates})


def GET_products_ratings(request):
    pg_result = psql("SELECT * FROM get_products_ratings()")
    return Response(data=pg_result.rows)


def GET_products(request):
    pg_result = psql("SELECT * FROM get_products()")
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
