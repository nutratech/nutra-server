from ..postgres import psql


def user_id_from_username(username):

    pg_result = psql("SELECT id FROM users WHERE username=%s", [username])

    # ERRORs
    if pg_result.err_msg or not pg_result.rows:
        return None

    return pg_result.row["id"]


def user_id_from_email(email):
    pass
