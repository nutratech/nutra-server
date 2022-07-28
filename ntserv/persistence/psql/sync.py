"""
Sync module, Postgres specific bits
NOTE: wip
"""
from ntserv.persistence.psql import psql


def sql_un_synced_rows(profile_guid: str, synced: int) -> list:
    """Returns un-synced rows"""
    pg_result = psql(
        "SELECT * FROM profile WHERE guid=%s AND updated>%s", [profile_guid, synced]
    )

    profiles = pg_result.rows

    return profiles


def sql_update_entities(_profile_guid: str, _entities: list) -> None:
    """TODO: method to update and apply patches to local store"""
    print("sql_update_entities() not implemented")
