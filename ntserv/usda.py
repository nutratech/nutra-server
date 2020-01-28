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
    pg_result = psql(
        "SELECT * FROM biometrics WHERE user_id IS NULL OR user_id=%s", [None]
    )

    return Response(data=pg_result.rows)


def POST_search(request):

    terms = request.json["terms"].split(",")
    query = " ".join(terms)

    scores = {f["id"]: fuzz.ratio(query, f["shrt_desc"]) for f in cache.food_des}
    scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:SEARCH_LIMIT]

    results = []
    for score in scores:
        pass
    return Response(data=results)


def GET_analyze(request):

    # TODO - handle recipe_ids also, see `db.js` old-code
    food_ids = request.args["food_ids"].split(",")
    food_ids = list(map(lambda x: int(x), food_ids))

    pg_result = psql("SELECT * FROM get_nutrients_by_food_ids(%s)", [food_ids])

    return Response(data=pg_result.rows)
