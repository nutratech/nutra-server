import json
from datetime import datetime

import shippo
from psycopg2.extras import Json
from py3dbp.main import Bin, Item, Packer

from .libserver import Response
from .postgres import psql
from .settings import SHIPPO_API_KEY
from .utils.account import user_id_from_username_or_email
from .utils.auth import AUTH_LEVEL_BASIC, AUTH_LEVEL_UNCONFIRMED, auth

# Set Shippo API key
shippo.config.api_key = SHIPPO_API_KEY

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


def GET_countries(request):
    pg_result = psql("SELECT * FROM get_countries_states()")
    return Response(data=pg_result.rows)


def POST_validate_addresses(request):
    addresses_ = request.json

    addresses = []
    for address_ in addresses_:
        try:
            address = shippo.Address.create(
                name=address_.get("name"),
                company=address_.get("company"),
                street1=address_["street1"],
                street2=address_.get("street2"),
                city=address_["city"],
                state=address_["state"],
                zip=address_.get("zip"),
                country=address_["country"],
                validate=True,
            )
        except Exception as e:
            # TODO: better bundle exceptions
            address = json.loads(json.dumps(e, default=lambda x: x.__dict__))
        addresses.append(address)

    return Response(data=addresses)


def POST_shipping_esimates(request):
    body = request.json
    user_id = body["user_id"]
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
        print(f"packer.add_bin(Bin('{c['tag']}', {l}, {w}, {h}, {c['weight_max']}))")
        packer.add_bin(bin)

    items_ = []
    for i in items:
        # TODO - include stock/inventory check at this point, or earlier in shop
        i = variants[i]
        l = i["dimensions"][0] / 2.54
        w = i["dimensions"][1] / 2.54
        h = i["dimensions"][2] / 2.54
        weight = i["weight"] / 454
        item = Item(i["denomination"], l, w, h, weight)
        print(
            f"packer.add_item(Item('{i['denomination']}', {round(l, 3)}, {round(w, 3)}, {round(h, 3)}, {round(weight, 3)}))"
        )
        items_.append(item)
        packer.add_item(item)

    packer.pack()

    bins = [bin for bin in packer.bins if bin.items]

    ########
    # SHIPPO
    parcels = []
    for bin in bins:
        parcel = {
            "name": bin.name,
            "length": bin.width,
            "width": bin.height,
            "height": bin.depth,
            "distance_unit": "in",
            # TODO resolve issue ( https://github.com/enzoruiz/3dbinpacking/issues/2 )
            # currently we are just assuming one package == sum( all items' weights )
            # "weight": sum([i.weight for i in bin.items]),
            "weight": round(sum([i.weight for i in items_]), 4),
            "mass_unit": "g",
        }
        parcels.append(parcel)

    shipment = shippo.Shipment.create(
        address_from=address_from,
        address_to=address,
        parcels=parcels,
        asynchronous=False,
    )

    # TODO: return order_id along with response object
    # TODO: support different bill/ship addresses
    pg_result = psql(
        "INSERT INTO orders (user_id, address_bill, address_ship, shippo_json) VALUES (%s, %s, %s, %s) RETURNING id",
        [user_id, Json(address_from), Json(address_from), Json(shipment)],
    )
    order_id = pg_result.row["id"]
    # TODO: bulk insert order_items
    for variant_id in set(items):
        quantity = items.count(variant_id)
        price = variants[variant_id]["price"]
        pg_result = psql(
            "INSERT INTO order_items (order_id, variant_id, quantity, price) VALUES (%s, %s, %s, %s) RETURNING order_id",
            [order_id, variant_id, quantity, price],
        )

    return Response(data=shipment)


def GET_products_ratings(request):
    pg_result = psql("SELECT * FROM get_products_ratings()")
    return Response(data=pg_result.rows)


def GET_products(request):
    pg_result = psql("SELECT * FROM get_products()")
    return Response(data=pg_result.rows)


# @auth
def POST_orders(request, level=AUTH_LEVEL_UNCONFIRMED, user_id=None):
    body = request.json
    user_id = int(body["user_id"])
    shipping_method = body["shipping_method"]
    shipping_price = float(body["shipping_price"])
    payment_method = body["payment_method"]
    address_bill = body["address_bill"]
    address_ship = body["address_ship"]
    items = body["items"]

    shipping_method_id = psql(
        "SELECT id FROM shipping_methods WHERE shipping_type=%s", [shipping_method]
    ).row["id"]

    pg_result = psql(
        "INSERT INTO orders (user_id, shipping_method_id, shipping_price, payment_method, address_bill, address_ship) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        [
            user_id,
            shipping_method_id,
            shipping_price,
            payment_method,
            Json(address_bill),
            Json(address_ship),
        ],
    )
    order_id = pg_result.row["id"]
    for id in set(items):
        quantity = items.count(id)
        price = psql("SELECT price FROM variants WHERE id=%s", [id]).row["price"]
        # TODO: handle error, for example change quantity to quanity and see how it fails silently
        pg_result = psql(
            "INSERT INTO order_items (order_id, variant_id, quantity, price) VALUES (%s, %s, %s, %s) RETURNING variant_id",
            [order_id, id, quantity, price],
        )
    return Response(data={"order_id": order_id})


def PATCH_orders(request):
    # TODO: better security against user's messing each others' orders and against DDoS
    body = request.json
    order_id = body["order_id"]
    email = body["email"]
    user_id = user_id_from_username_or_email(email)
    if not user_id:
        return Response(data={"error": "No such user"}, code=400)

    # Create patch-order object
    patcher = {
        "updated": int(datetime.now().timestamp()),
    }
    for k in body.keys():
        if not k in patcher and not (k == "order_id" or k == "email"):
            patcher[k] = body[k]

    # Parameterize SQL and UPDATE
    parameters = ", ".join([f"{k}=%s" for k in patcher.keys()])
    values = list(patcher.values())
    values.extend([order_id, user_id])

    pg_result = psql(
        f"UPDATE orders SET {parameters} WHERE id=%s AND user_id=%s  RETURNING status",
        values,
    )

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

    product_id = request.view_args["id"]
    pg_result = psql("SELECT * FROM get_product_reviews(%s)", [product_id])

    return Response(data=pg_result.rows)
