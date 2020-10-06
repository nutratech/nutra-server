from ...postgres import psql


def sql_unsynced_rows(profile_guid, synced):
    pg_result = psql(
        "SELECT * FROM profiles WHERE guid=%s AND updated>%s", [profile_guid, synced]
    )

    profiles = pg_result.rows

    return profiles


def sql_update_entities(profile_guid, entities):
    print("sql_update_entities() not implemented")
    return None
