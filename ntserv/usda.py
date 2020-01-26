from .libserver import Response
from .postgres import psql


def GET_fdgrp(request):

    pg_result = psql("SELECT * FROM fdgrp")

    return Response(data=pg_result.rows)
