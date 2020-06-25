from datetime import datetime

from psycopg2.extras import Json
from py3dbp.main import Bin, Item, Packer
from tabulate import tabulate
from usps import (
    LABEL_ZPL,
    SERVICE_FIRST_CLASS,
    SERVICE_PARCEL_SELECT,
    SERVICE_PRIORITY,
    SERVICE_PRIORITY_EXPRESS,
    Address,
    USPSApi,
)

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
from .utils.cache import get_shipping_containers, get_variants

# Set USPS API key
usps = USPSApi(USPS_API_KEY)

# address_from = {
#     # "name": "Post Office",
#     # "company": "USPS",
#     "street1": "100 Renaissance Center",
#     "street2": "Ste 1014",
#     "city": "Detroit",
#     "state": "MI",
#     "zip": 48243,
#     "country": "US",
#     # "phone": "+1 313 259 3219.",
#     # "email": "postalone@email.usps.gov",
#     # "metadata": "Neither snow nor rain nor heat nor gloom of night stays these couriers from the swift completion of their appointed rounds",
# }

address_from = Address(
    name="Post Office",
    address_1="100 Renaissance Center",
    address_2="Ste 1014",
    city="Detroit",
    state="MI",
    zipcode="48243",
)


def POST_validate_addresses(request):
    addresses = list(request.json)

    validations = []
    for a in addresses:
        if not a["country"] == "US":
            return Response(
                data={"error": "Sorry, only support shipping to U.S. for now :["},
                code=400,
            )

        address = Address(
            a["name"],
            a["street1"],
            a["city"],
            a["state"],
            str(a["zip"]),
            zipcode_ext=a.get("zipcode_ext", ""),
            company=a.get("company", ""),
            address_2=a.get("address_2", ""),
            phone=a.get("phone", ""),
        )
        validation = usps.validate_address(address)
        validations.append(validation.result["AddressValidateResponse"])

    return Response(data=validations)


def POST_shipping_esimates(request):
    body = request.json
    # user_id = body["user_id"]
    address_to = body["address"]
    items = body["items"]

    #############
    # 3D bin-pack
    packer = Packer()

    # TODO: DHL box standards for international shipments
    containers = get_shipping_containers()
    variants = get_variants()

    for c in containers.values():
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

    packer.pack(bigger_first=True)

    bins = [bin for bin in packer.bins if not bin.unfitted_items]

    # Make solution customer friendly
    # TODO: less simplistic handling than min(volume), e.g. international, different shippint speeds, costs.
    smallest_bin = min(bins, key=lambda b: b.depth * b.height * b.width)
    solution = next(
        (
            # Gets the smallest_bin by matching name (a string)
            c
            for c in containers.values()
            if " ".join([c["courier"], c["method"], c["container"]])
            == smallest_bin.name
        ),
        None,
    )

    # TODO: make real API call to shipping estimate
    address_to = Address(
        name=address_to["name"],
        address_1=address_to["street1"],
        address_2=address_to.get("street2"),
        city=address_to["city"],
        state=address_to["state"],
        zipcode=str(address_to["zip"]),
    )
    weight = 12
    label = usps.create_label(
        address_to, address_from, weight, SERVICE_PRIORITY, LABEL_ZPL
    )
    print(label.result)

    return Response(data=solution)


# TODO: generic endpoint for get_function_name() or select_table_name()
# the front end can then pass in a query or route param, and
# we reduce dozens of separate endpoints here to just 2 or 3 generic functions
def GET_categories(request):
    pg_result = psql("SELECT * FROM get_categories()")
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


# @auth
def GET_products_profits(request, level=AUTH_LEVEL_FULL_ADMIN, user_id=None):

    pg_result = psql("SELECT id, name FROM products WHERE shippable=TRUE")
    products = pg_result.rows

    pg_result = psql("SELECT id, product_id, grams, denomination, price FROM variants")
    variants = {}
    for r in pg_result.rows:
        id = r["product_id"]
        if id not in variants:
            variants[id] = []
        variants[id].append(r)

    pg_result = psql("SELECT * FROM ingredients")
    ingredients = {r["id"]: r for r in pg_result.rows}

    pg_result = psql("SELECT * FROM product_ingredients")
    product_ingredients = {}
    for entry in pg_result.rows:
        id = entry["product_id"]
        if id not in product_ingredients:
            product_ingredients[id] = []
        product_ingredients[id].append(
            {"ingredient_id": entry["ingredient_id"], "mg": entry["mg"]}
        )

    ###################
    # Calculate costs
    for p in products:
        id = p["id"]
        if id not in product_ingredients:
            print(f"no ingredients for {p['name']}")
            p["cost_per_kg"] = None
            continue
        ingreds = product_ingredients[id]
        tot_weight = sum(i["mg"] for i in ingreds)
        for i in ingreds:
            i["relative_perc"] = i["mg"] / tot_weight

        p["cost_per_kg"] = sum(
            i["relative_perc"] * ingredients[i["ingredient_id"]]["cost_per_kg"]
            for i in ingreds
        )
        # Revenue per variant per kg
        for v in variants[id]:
            kg = v["grams"] / 1000
            print(v)
            p[v["denomination"]] = v["price"] / kg

    table = tabulate(products, headers="keys")
    print(table)

    return f"""<pre>
{table}
</pre>
"""


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
