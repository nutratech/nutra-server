import sanic

from ntserv.persistence.psql.sync import sql_unsynced_rows, sql_update_entities
from ntserv.utils.auth import auth
from ntserv.utils.libserver import NotImplemented501Response, Success200Response


@auth
def opt_sync(*args: sanic.Request) -> sanic.HTTPResponse:
    """Used to GET and POST local saved data to remote"""
    request = args[0]

    # FIXME: fix this, broke during migration from Flask to Sanic
    method = request.environ["REQUEST_METHOD"]  # type: ignore

    if method == "GET":
        profile_guid = request.args["uid"]
        synced = int(request.args["last_sync"])

        profiles = sql_unsynced_rows(profile_guid, synced)
        return Success200Response(data={"profiles": profiles})
    if method == "POST":
        profile_guid = request.json["uid"]
        entities = request.json["entities"]
        sql_update_entities(profile_guid, entities)
        return Success200Response()

    return NotImplemented501Response()
