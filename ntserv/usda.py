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
