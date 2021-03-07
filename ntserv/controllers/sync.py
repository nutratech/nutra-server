from ..libserver import Success200Response
from ..services.psql.sync import sql_update_entities, sql_unsynced_rows
from ..utils.auth import auth, AUTH_LEVEL_BASIC


@auth
def OPT_sync(request, level=AUTH_LEVEL_BASIC, user_id=None):
    """ Used to GET and POST local saved data to remote """

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
