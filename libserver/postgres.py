import psycopg2

from .settings import (
    PSQL_DATABASE,
    PSQL_SCHEMA,
    PSQL_USER,
    PSQL_PASSWORD,
    PSQL_HOST,
)


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
        cmd = cur.mogrify(cmd, params)
    print(f"[psql] {cmd}")

    try:
        cur.execute(cmd, params)
        con.commit()
    except:
        con.rollback()

    print(f"     {cur.statusmessage}")
    result = None
    try:
        result = cur.fetchall()
    except:
        query = cur.query.decode()
        result = cur.statusmessage
        print(f"WARN: no result: {query}")

    cur.close()
    return result
