import jwt
import pyshipping
import shippo
import stripe

from .libserver import Response
from .postgres import psql
from .settings import JWT_SECRET, SHIPPO_API_KEY, STRIPE_API_KEY
from .utils.account import user_id_from_username
from .utils.auth import AUTH_LEVEL_BASIC, auth

# Set Stripe & Shippo API keys
shippo.config.api_key = SHIPPO_API_KEY
stripe.api_key = STRIPE_API_KEY

address_from = {
    "name": "Shippo Team",
    "street1": "965 Mission St",
    "street2": "Unit 480",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94103",
    "country": "US",
    "phone": "+1 555 341 9393",
}


def GET_countries(request):
    pg_result = psql("SELECT * FROM get_countries_states()")
    return Response(data=pg_result.rows)


def POST_shipping_esimates(request):
    body = request.json
    address = body["address"]
    products = body["products"]

    # Example address_to object dict
    # The complete refence for the address object is available here: https://goshippo.com/docs/reference#addresses

    address_to = {
        "name": "Shippo Friend",
        "street1": "1092 Indian Summer Ct",
        "city": "San Jose",
        "state": "CA",
        "zip": "95122",
        "country": "US",
        "phone": "+1 555 341 9393",
    }

    # parcel object dict
    # The complete reference for parcel object is here: https://goshippo.com/docs/reference#parcels
    parcel = {
        "length": "5",
        "width": "5",
        "height": "5",
        "distance_unit": "in",
        "weight": "2",
        "mass_unit": "lb",
    }

    # Example shipment object
    # For complete reference to the shipment object: https://goshippo.com/docs/reference#shipments
    # This object has asynchronous=False, indicating that the function will wait until all rates are generated before it returns.
    # By default, Shippo handles responses asynchronously. However this will be depreciated soon. Learn more: https://goshippo.com/docs/async
    shipment = shippo.Shipment.create(
        address_from=address_from,
        address_to=address_to,
        parcels=[parcel],
        asynchronous=False,
    )

    pg_result = psql("SELECT * FROM shipping_methods WHERE is_physical=TRUE")
    methods = pg_result.rows
    print(methods)
    return Response(data=methods)


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
