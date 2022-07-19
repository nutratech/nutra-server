import sanic

from ntserv.persistence.psql.sync import sql_unsynced_rows, sql_update_entities
from ntserv.utils.auth import AUTH_LEVEL_BASIC, auth
from ntserv.utils.libserver import NotImplemented501Response, Success200Response

# NOTE: wip
# TODO: magic number


@auth
def opt_sync(
    request: sanic.Request, level: int = AUTH_LEVEL_BASIC, user_id: int = -65536
) -> sanic.HTTPResponse:
    """Used to GET and POST local saved data to remote"""

    # TODO: fix this, broke during migration from Flask to Sanic
    method = request.environ["REQUEST_METHOD"]

    if method == "GET":
        profile_guid = request.args["uid"]
        synced = int(request.args["last_sync"])

        profiles = sql_unsynced_rows(profile_guid, synced)
        return Success200Response(data={"profiles": profiles})
    elif method == "POST":
        profile_guid = request.json["uid"]
        entities = request.json["entities"]
        sql_update_entities(profile_guid, entities)
        return Success200Response()

    return NotImplemented501Response()
