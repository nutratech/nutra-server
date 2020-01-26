import sys

import psycopg2

from .settings import PSQL_DATABASE, PSQL_HOST, PSQL_PASSWORD, PSQL_SCHEMA, PSQL_USER

# Initialize connection
con = psycopg2.connect(
    database=PSQL_DATABASE,
    user=PSQL_USER,
    password=PSQL_PASSWORD,
    host=PSQL_HOST,
    port="5432",
    options=f"-c search_path={PSQL_SCHEMA}",
)

print(
    f"[Connected to Postgre DB]    postgresql://{PSQL_USER}:{PSQL_PASSWORD}@{PSQL_HOST}:5432/{PSQL_DATABASE}",
)
print(f"[psql] USE SCHEMA {PSQL_SCHEMA};")


def psql(cmd, params=None):

    cur = con.cursor()

    # Print cmd
    if params:
        cmd = cur.mogrify(cmd, params).decode("utf-8")
    print(f"[psql] {cmd}")

    try:
        cur.execute(cmd)
        con.commit()
        cur.close()
    except psycopg2.Error as err:
        # https://kb.objectrocket.com/postgresql/python-error-handling-with-the-psycopg2-postgresql-adapter-645
        print(f"[psql] {err.pgerror}")
        cur.close()
        con.rollback()
        return None

    result = cur.statusmessage
    print(f"[psql] {result}")

    return result
