from .libserver import Response
from .postgres import psql


def GET_fdgrp(request):
    pg_result = psql("SELECT * FROM fdgrp")

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


def GET_search(request):

    terms = request.args["terms"].split(",")

    search_query = " | ".join(terms)
    vector_query = "%" + "%,%".join(terms) + "%"

    pg_result = psql(
        "SELECT * FROM search_foods_by_name(%s, %s)", [search_query, vector_query]
    )

    return Response(data=pg_result.rows)
