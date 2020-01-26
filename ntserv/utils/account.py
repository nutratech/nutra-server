from ..postgres import psql


def user_id_from_username(username):

    pg_result = psql("SELECT id FROM users WHERE username=%s", [username])

    # ERRORs
    if pg_result.err_msg:
        return None

    return pg_result.row[0]


def user_id_from_email(email):
    pass
