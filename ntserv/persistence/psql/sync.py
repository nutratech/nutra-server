from ntserv.persistence.psql import psql

# NOTE: wip


def sql_unsynced_rows(profile_guid: str, synced: int) -> list:
    pg_result = psql(
        "SELECT * FROM profile WHERE guid=%s AND updated>%s", [profile_guid, synced]
    )

    profiles = pg_result.rows

    return profiles


def sql_update_entities(profile_guid: str, entities: list) -> None:
    print("sql_update_entities() not implemented")
