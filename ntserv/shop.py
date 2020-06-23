from datetime import datetime

from psycopg2.extras import Json
from py3dbp.main import Bin, Item, Packer
from usps import Address, USPSApi

from .libserver import Response
from .postgres import psql
from .settings import USPS_API_KEY
from .utils.auth import (
    AUTH_LEVEL_BASIC,
    AUTH_LEVEL_FULL_ADMIN,
    AUTH_LEVEL_UNCONFIRMED,
    auth,
    check_request,
)

# Set USPS API key
usps = USPSApi(USPS_API_KEY)

address_from = {
    # "name": "Post Office",
    # "company": "USPS",
    "street1": "100 Renaissance Center",
    "street2": "Ste 1014",
    "city": "Detroit",
    "state": "MI",
    "zip": 48243,
    "country": "US",
    # "phone": "+1 313 259 3219.",
    # "email": "postalone@email.usps.gov",
    # "metadata": "Neither snow nor rain nor heat nor gloom of night stays these couriers from the swift completion of their appointed rounds",
}


def POST_shipping_esimates(request):
    body = request.json
    # user_id = body["user_id"]
    address = body["address"]
    items = body["items"]

    # Query DB for products, shipping methods and containers
    pg_result = psql("SELECT * FROM variants")
    variants = {r["id"]: r for r in pg_result.rows}
    pg_result = psql("SELECT * FROM shipping_containers")
    containers = pg_result.rows

    #############
    # 3D bin-pack
    packer = Packer()

    # TODO: DHL box standards for international shipments

    for c in containers:
        l = c["dimensions"][0] * 2.54  # inches --> cm
        w = c["dimensions"][1] * 2.54
        h = c["dimensions"][2] * 2.54
        weight = c["weight_max"] * 454  # pounds -->
        tag = " ".join([c["courier"], c["method"], c["container"]])
        bin = Bin(tag, l, w, h, weight)
        print(f"packer.add_bin(Bin('{tag}', {l}, {w}, {h}, {weight}))")
        packer.add_bin(bin)

    items_ = []
    for i in items:
        # TODO - include stock/inventory check at this point, or earlier in shop
        i = variants[i]
        l = i["dimensions"][0]  # cm
        w = i["dimensions"][1]
        h = i["dimensions"][2]
        weight = i["weight"]  # grams
        item = Item(i["denomination"], l, w, h, weight)
        print(
            f"packer.add_item(Item('{i['denomination']}', {round(l, 3)}, {round(w, 3)}, {round(h, 3)}, {round(weight, 3)}))"
        )
        items_.append(item)
        packer.add_item(item)

    packer.pack()

    bins = [bin for bin in packer.bins if bin.items]

    # ########
    # # SHIPPO
    # parcels = []
    # for bin in bins:
    #     parcel = {
    #         "name": bin.name,
    #         "length": float(bin.width),
    #         "width": float(bin.height),
    #         "height": float(bin.depth),
    #         "distance_unit": "cm",
    #         # TODO resolve issue ( https://github.com/enzoruiz/3dbinpacking/issues/2 )
    #         # currently we are just assuming one package == sum( all items' weights )
    #         # "weight": sum([i.weight for i in bin.items]),
    #         "weight": float(round(sum([i.weight for i in items_]), 4)),
    #         "mass_unit": "g",
    #     }
    #     parcels.append(parcel)

    # shipment = shippo.Shipment.create(
    #     address_from=address_from,
    #     address_to=address,
    #     parcels=parcels,
    #     asynchronous=False,
    # )

    shipment = None

    # TODO - reduce down to subset of shipping options (more user-friendly?)
    return Response(data=shipment)


def GET_pcategories(request):
    pg_result = psql("SELECT * FROM get_pcategories()")
    return Response(data=pg_result.rows)


def GET_products(request):
    pg_result = psql("SELECT * FROM get_products()")
    return Response(data=pg_result.rows)


def POST_orders(request):
    body = request.json

    email = body.get("email")

    address_bill = body["address_bill"]
    address_ship = body.get("address_ship")

    shipping_method = body["shipping_method"]
    shipping_price = float(body["shipping_price"])

    items = body["items"]

    if not email:
        # Check authorization
        authr, error = check_request(request)
        if not authr or authr.expired or authr.auth_level < AUTH_LEVEL_UNCONFIRMED:
            return Response(data={"error": error}, code=401)
        # Set user_id
        user_id = authr.id
    else:
        user_id = None

    # Insert order
    pg_result = psql(
        "INSERT INTO orders (user_id, email, address_bill, address_ship, shipping_method, shipping_price) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        [
            user_id,
            email,
            Json(address_bill),
            Json(address_ship),
            shipping_method,
            shipping_price,
        ],
    )
    # Insert items
    order_id = pg_result.row["id"]
    for variant_id in set(items):
        quantity = items.count(variant_id)
        price = psql("SELECT price FROM variants WHERE id=%s", [variant_id]).row[
            "price"
        ]
        # TODO: handle error, for example change quantity to quanity and see how it fails silently
        pg_result = psql(
            "INSERT INTO order_items (order_id, variant_id, quantity, price) VALUES (%s, %s, %s, %s) RETURNING variant_id",
            [order_id, variant_id, quantity, price],
        )
    return Response(data={"order_id": order_id})


@auth
def GET_orders(request, level=AUTH_LEVEL_UNCONFIRMED, user_id=None):
    # id = int(request.view_args["id"])

    pg_result = psql("SELECT * FROM get_orders(%s)", [user_id])

    return Response(data=pg_result.rows)


@auth
def PATCH_orders_admin(request, level=AUTH_LEVEL_FULL_ADMIN, user_id=None):
    body = request.json
    order_id = int(body["order_id"])

    # Create patch-order object
    patcher = {
        "updated": int(datetime.now().timestamp()),
    }
    for k in body.keys():
        if k not in patcher and not (k == "order_id" or k == "email"):
            patcher[k] = body[k]

    # Parameterize SQL and UPDATE
    assignments = ", ".join([f"{k}=%s" for k in patcher.keys()])
    conditions = "id=%s"
    parameters = list(patcher.values())
    parameters.extend([order_id])
    pg_result = psql(
        f"UPDATE orders SET {assignments} WHERE {conditions} RETURNING status",
        parameters,
    )

    # TODO: send confirmation email to both us (admins) and user

    return Response(data=pg_result.row)


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

    product_id = int(request.view_args["id"])
    pg_result = psql("SELECT * FROM get_product_reviews(%s)", [product_id])

    return Response(data=pg_result.rows)
