import csv
import io
import math

from fuzzywuzzy import fuzz
from tabulate import tabulate

from .libserver import Response
from .postgres import psql
from .settings import NUTR_ID_KCAL, NUTR_IDS_AMINOS, NUTR_IDS_FLAVONES, SEARCH_LIMIT
from .utils import cache


def GET_calc_bodyfat(request):
    body = request.json

    gender = body["gender"]
    age = body["age"]
    height = body["height"]

    # Navy measurements
    waist = body.get("waist")
    if gender == "female":
        hip = body.get("hip")
    neck = body.get("neck")

    # 3-site calipers
    chest = body.get("chest")
    ab = body.get("ab")
    thigh = body.get("thigh")

    # 7-site calipers
    tricep = body.get("tricep")
    sub = body.get("sub")
    sup = body.get("sup")
    mid = body.get("mid")

    # Navy test
    if gender == "male":
        denom = (
            1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(height)
        )
    elif gender == "female":
        denom = (
            1.29579
            - 0.35004 * math.log10(waist + hip - neck)
            + 0.22100 * math.log10(height)
        )
    else:
        denom = 1
    navy = round(495 / denom - 450, 2)

    # 3-site test
    s3 = chest + ab + thigh
    if gender == "male":
        denom = 1.10938 - 0.0008267 * s3 + 0.0000016 * s3 * s3 - 0.0002574 * age
    elif gender == "female":
        denom = 1.089733 - 0.0009245 * s3 + 0.0000025 * s3 * s3 - 0.0000979 * age
    else:
        denom = 1
    three_site = round(495 / denom - 450, 2)

    # 7-site test
    s7 = chest + ab + thigh + tricep + sub + sup + mid
    if gender == "male":
        denom = 1.112 - 0.00043499 * s7 + 0.00000055 * s7 * s7 - 0.00028826 * age
    elif gender == "female":
        denom = 1.097 - 0.00046971 * s7 + 0.00000056 * s7 * s7 - 0.00012828 * age
    else:
        denom = 1
    seven_site = round(495 / denom - 450, 2)

    return Response(
        data={"navy": navy, "three-site": three_site, "seven-site": seven_site}
    )


def GET_calc_lblimits(request):
    body = request.json
    height = body["height"]

    desired_bf = body.get("desired-bf")

    wrist = body.get("wrist")
    ankle = body.get("ankle")

    # Martin Berkhan
    min = round((height - 102) * 2.205, 1)
    max = round((height - 98) * 2.205, 1)
    mb = {"notes": "Contest shape (5-6%)", "weight": f"{min} ~ {max} lbs"}

    # Eric Helms
    min = round(4851.00 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
    max = round(5402.25 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
    eh = {"notes": f"{desired_bf}% bodyfat", "weight": f"{min} ~ {max} lbs"}

    # Casey Butt, PhD
    h = height / 2.54
    w = wrist / 2.54
    a = ankle / 2.54
    lbm = round(
        h ** (3 / 2)
        * (math.sqrt(w) / 22.6670 + math.sqrt(a) / 17.0104)
        * (1 + desired_bf / 224),
        1,
    )
    weight = round(lbm / (1 - desired_bf / 100), 1)
    cb = {
        "notes": f"{desired_bf}% bodyfat",
        "lbm": f"{lbm} lbs",
        "weight": f"{weight} lbs",
        "chest": round(1.6817 * w + 1.3759 * a + 0.3314 * h, 2),
        "arm": round(1.2033 * w + 0.1236 * h, 2),
        "forearm": round(0.9626 * w + 0.0989 * h, 2),
        "neck": round(1.1424 * w + 0.1236 * h, 2),
        "thigh": round(1.3868 * a + 0.1805 * h, 2),
        "calf": round(0.9298 * a + 0.1210 * h, 2),
    }
    return Response(data={"martin-berkhan": mb, "eric-helms": eh, "casey-butt": cb})


# ---------------------------------
# USDA Food functions
# ---------------------------------
def GET_data_src(request):
    pg_result = psql("SELECT * FROM data_src")
    return Response(data=pg_result.rows)


def GET_fdgrp(request):
    pg_result = psql("SELECT * FROM fdgrp")
    return Response(data=pg_result.rows)


def GET_serving_sizes(request):

    id = request.args["food_id"]
    pg_result = psql("SELECT * FROM get_food_servings(%s)", [id])
    return Response(data=pg_result.rows)


def GET_nutrients(request, response_type="JSON"):
    pg_result = psql("SELECT * FROM get_nutrients_overview()")

    if response_type == "JSON":
        return Response(data=pg_result.rows)
    else:  # HTML
        table = tabulate(pg_result.rows, headers="keys", tablefmt="orgtbl")
        return f"<pre>{table}</pre>"


# def GET_exercises(request):
#     pg_result = psql("SELECT * FROM exercises")
#     return Response(data=pg_result.rows)


# def GET_biometrics(request):
#     pg_result = psql("SELECT * FROM biometrics")
#     return Response(data=pg_result.rows)


def GET_foods_search(request, response_type="JSON"):

    terms = request.args["terms"].split(",")
    query = " ".join(terms)

    scores = {
        f["id"]: fuzz.token_set_ratio(query, f["long_desc"])
        for f in cache.food_des.values()
    }
    scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:SEARCH_LIMIT]
    ids = [s[0] for s in scores]
    pg_result = psql("SELECT * FROM get_nutrients_by_food_ids(%s)", [ids])
    nut_data = {nd["food_id"]: nd["nutrients"] for nd in pg_result.rows}

    results = []
    for score in scores:
        # Tally each score
        food_id = score[0]

        score = score[1]
        item = cache.food_des[food_id]
        fdgrp_id = item["fdgrp_id"]
        data_src_id = item["data_src_id"]

        nutrients = {nd["nutr_id"]: nd for nd in nut_data[food_id]}

        result = {
            "food_id": food_id,
            "fdgrp_id": fdgrp_id,
            "fdgrp_desc": cache.fdgrp[fdgrp_id]["fdgrp_desc"],
            "data_src": cache.data_src[data_src_id]["name"],
            "long_desc": item["long_desc"],
            "score": score,
            "nutrients": nutrients,
        }
        # Add result to list
        results.append(result)

    if response_type == "JSON":
        return Response(data=results)
    else:  # HTML

        def tabulate_results():
            """ Copied from CLI repo to package up results, TODO: make into separate core util """
            headers = [
                "food_id",
                "food_name",
                "kcal",
                "# nutrients",
                "Aminos",
                "Flavones",
                "fdgrp_desc",
            ]
            rows = []
            for i, r in enumerate(results):
                food_id = r["food_id"]
                food_name = r["long_desc"][:45]
                fdgrp_desc = r["fdgrp_desc"]

                nutrients = r["nutrients"]
                kcal = nutrients.get(str(NUTR_ID_KCAL))
                kcal = kcal["nutr_val"] if kcal else None
                len_aminos = len(
                    [
                        nutrients[n_id]
                        for n_id in nutrients
                        if int(n_id) in NUTR_IDS_AMINOS
                    ]
                )
                len_flavones = len(
                    [
                        nutrients[n_id]
                        for n_id in nutrients
                        if int(n_id) in NUTR_IDS_FLAVONES
                    ]
                )

                row = [
                    food_id,
                    food_name,
                    kcal,
                    len(nutrients),
                    len_aminos,
                    len_flavones,
                    fdgrp_desc,
                ]
                rows.append(row)
            return tabulate(rows, headers=headers, tablefmt="orgtbl")

        # table = tabulate(results, headers="keys", tablefmt="orgtbl")
        table = tabulate_results()
        return f"<pre>{table}</pre>"


def GET_foods_sort(request, response_type="JSON"):
    id = request.args["nutr_id"]
    # TODO - filter by food group?  Makes more sense here than /search
    pg_result = psql("SELECT * FROM sort_foods_by_nutrient_id(%s)", [id])

    if response_type == "JSON":
        return Response(data=pg_result.rows)
    else:  # HTML
        table = tabulate(pg_result.rows, headers="keys", tablefmt="orgtbl")
        return f"<pre>{table}</pre>"


def GET_foods_analyze(request, response_type="JSON"):

    # TODO - handle recipe_ids also, see `db.js` old-code
    food_ids = request.args["food_ids"].split(",")
    food_ids = list(map(lambda x: int(x), food_ids))

    pg_result = psql("SELECT * FROM get_nutrients_by_food_ids(%s)", [food_ids])
    analyses = pg_result.rows
    pg_result = psql("SELECT * FROM get_foods_servings(%s)", [food_ids])
    servings = pg_result.rows
    food_des = [x for x in cache.food_des.values() if x["id"] in food_ids]

    if response_type == "JSON":
        return Response(
            data={"analyses": analyses, "servings": servings, "food_des": food_des}
        )
    else:  # HTML

        def tabulate_results():
            """ Copied from CLI repo to package up results, TODO: make into separate core util """

            # Get RDAs
            rdas = cache.nutr_def

            # Gather analyses
            tables = []
            for food in analyses:
                table = str(
                    "\n======================================\n"
                    f"==> {food['long_desc']} ({food['food_id']})\n"
                    "======================================\n",
                )
                # TODO: include servings table as separate info above

                headers = ["nutrient", "amount", "units", "rda"]
                rows = []
                food_nutes = {x["nutr_id"]: x for x in food["nutrients"]}
                for id, nute in food_nutes.items():
                    if not rdas[id]["rda"]:
                        continue

                    amount = food_nutes[id]["nutr_val"]
                    if not amount:
                        continue
                    rda_ratio = round(amount / rdas[id]["rda"] * 100, 1)
                    rows.append(
                        [nute["nutr_desc"], amount, rdas[id]["units"], f"{rda_ratio}%"]
                    )
                table += tabulate(rows, headers=headers, tablefmt="orgtbl")
                tables.append(table)
            return tables

        results = tabulate_results()
        text = "\n".join(results)
        return f"<pre>{text}</pre>"


def GET_foods_analyze_csv(request):

    # Get CSV file bytes off request
    food_log_csv_file = io.TextIOWrapper(request.files["input.csv"])
    rda_csv_file = io.TextIOWrapper(request.files["rdas.csv"])

    food_log_csv_input = csv.DictReader(food_log_csv_file)
    rda_csv_input = csv.DictReader(rda_csv_file)

    # Parse CSV files
    food_log = []
    rdas = []
    for row in food_log_csv_input:
        food_log.append(row)
    for row in rda_csv_input:
        rdas.append(row)

    # Extract data
    # {food_id: grams}
    foods_amounts = {int(x["id"]): float(x["grams"]) for x in food_log if x["id"]}
    # {nutr_id: rda_val}
    rda_pairs = {int(x["id"]): float(x["rda"]) for x in rdas}

    # Analyze foods
    pg_result = psql(
        "SELECT * FROM get_nutrients_by_food_ids(%s)", [list(foods_amounts.keys())]
    )
    foods_nutrients = {x["food_id"]: x["nutrients"] for x in pg_result.rows}
    nutrient_totals = {}
    for food_nutrients in foods_nutrients.values():
        for food_nutrient in food_nutrients:
            id = food_nutrient["nutr_id"]
            if id not in nutrient_totals:
                nutrient_totals[id] = 0
            nutrient_totals[id] += food_nutrient["nutr_val"]

    return Response(
        data={
            "foods_amounts": foods_amounts,
            "rdas": rda_pairs,
            "food_nutrients": food_nutrients,
            "nutrient_totals": nutrient_totals,
        }
    )


# def GET_foods(request):
#     food_des = get_food_des()
#     return Response(data=food_des)
