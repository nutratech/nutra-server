from fuzzywuzzy import fuzz

from .libserver import Response
from .postgres import psql
from .settings import SEARCH_LIMIT
from .utils import cache


def GET_fdgrp(request):
    pg_result = psql("SELECT * FROM fdgrp")

    return Response(data=pg_result.rows)


def GET_serving_sizes(request):

    food_id = request.args["food_id"]
    pg_result = psql("SELECT * FROM get_food_servings(%s)", [food_id])

    return Response(data=pg_result.rows)


def GET_nutrients(request):
    pg_result = psql("SELECT * FROM nutr_def")

    return Response(data=pg_result.rows)


def GET_exercises(request):
    pg_result = psql("SELECT * FROM exercises")

    return Response(data=pg_result.rows)


def GET_biometrics(request):
    pg_result = psql("SELECT * FROM biometrics")

    return Response(data=pg_result.rows)


def GET_search(request):

    terms = request.args["terms"].split(",")
    query = " ".join(terms)

    scores = {
        f["id"]: fuzz.token_set_ratio(query, f["long_desc"])
        for f in cache.food_des.values()
    }
    scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:SEARCH_LIMIT]

    results = []
    for score in scores:
        # Tally each score
        id = score[0]
        score = score[1]
        item = cache.food_des[id]
        fdgrp_id = item["fdgrp_id"]
        result = {
            "food_id": id,
            "fdgrp_desc": cache.fdgrp[fdgrp_id]["fdgrp_desc"],
            "long_desc": item["long_desc"],
            "score": score,
        }
        # Add result to list
        results.append(result)

    return Response(data=results)


def GET_analyze(request):

    # TODO - handle recipe_ids also, see `db.js` old-code
    food_ids = request.args["food_ids"].split(",")
    food_ids = list(map(lambda x: int(x), food_ids))

    pg_result = psql("SELECT * FROM get_nutrients_by_food_ids(%s)", [food_ids])

    return Response(data=pg_result.rows)
