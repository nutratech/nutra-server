import psycopg2
import psycopg2.extras
import sanic.response

from ntserv import __db_target_ntdb__
from ntserv.env import PSQL_DATABASE, PSQL_HOST, PSQL_PASSWORD, PSQL_SCHEMA, PSQL_USER
from ntserv.utils.libserver import ServerError500Response, Success200Response
from ntserv.utils.logger import get_logger

_logger = get_logger(__name__)


class PgResult:
    def __init__(self, query: str, err_msg=str()) -> None:
        """Defines a convenient result for `psql()`"""

        self.query = query

        # TODO: do these belong in init or update? Do we pass in rows to __init__ even?
        self.rowcount = 0
        self.row: dict = {}
        self.rows: list = []

        self.msg = str()
        self.err_msg = err_msg

    @property
    def http_response_error(self) -> sanic.response.HTTPResponse:
        """Used ONLY for ERRORS"""

        return ServerError500Response(
            data={"errMsg": "General database error (Postgres)", "stack": self.err_msg}
        )

    def set_rows(self, cur: psycopg2._psycopg.cursor) -> None:
        """Sets the DictCursor rows based on cur.fetchall()"""

        self.rowcount = cur.rowcount
        # WARN: some exception, see below usage of set_rows()
        fetchall = cur.fetchall()

        self.rows = []

        if len(fetchall):
            keys = list(fetchall[0]._index.keys())

            # Build dict from named tuple
            for entry in fetchall:
                row = {}
                for i, element in enumerate(entry):
                    key = keys[i]
                    row[key] = element
                self.rows.append(row)

            # Set first row
            self.row = self.rows[0]


def build_con(
    database=PSQL_DATABASE,
    user=PSQL_USER,
    password=PSQL_PASSWORD,
    host=PSQL_HOST,
    port="5432",
    options=f"-c search_path={PSQL_SCHEMA}",
    connect_timeout=8,
) -> psycopg2._psycopg.connection:
    """Build and return con"""
    con = psycopg2.connect(
        database=database,
        user=user,
        password=password,
        host=host,
        port=port,
        options=options,
        connect_timeout=connect_timeout,
    )

    _url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    _logger.debug("psql %s", _url)

    return con


def psql(query, params=None) -> PgResult:
    # TODO:  mandatory "RETURNING id" after all "INSERTS"

    # Initialize connection
    try:
        con = build_con()
    except psycopg2.OperationalError as err:
        _logger.error("build_con() failed: %s", repr(err))
        return PgResult(query=str(), err_msg="failed to build con")

    # Build cursor
    try:
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    except AttributeError as err:
        _logger.error("con.cursor() failed: %s", repr(err))
        return PgResult(query=str(), err_msg="failed to build cursor")

    # Print query (mogrify, if not many)
    if params:
        query = cur.mogrify(query, params).decode("utf-8")
    _logger.debug("[psql]   %s;", query)

    # init result object
    result = PgResult(query)

    # --------------------------------------------
    # Attempt query
    # --------------------------------------------
    try:
        # TODO: support cur.executemany()
        cur.execute(query)
    except psycopg2.Error as err:
        # https://kb.objectrocket.com/postgresql/python-error-handling-with-the-psycopg2-postgresql-adapter-645
        _logger.warning("[psql]   %s", err.pgerror)

        # Set err_msg
        result.err_msg = err.pgerror

        # Roll back
        con.rollback()
        cur.close()
        con.close()

        # Return empty result instance
        return result

    # --------------------------------------------
    # Extract result
    # --------------------------------------------
    try:
        result.set_rows(cur)
    except psycopg2.ProgrammingError as err_prog:
        # WARN: err_prog: no results to fetch
        _logger.debug("Extract fetchall / commit failed: %s", repr(err_prog))

    # Commit
    con.commit()
    cur.close()
    con.close()

    # Set return message
    result.msg = cur.statusmessage
    _logger.debug("[psql]   %s", result.msg)

    return result


def verify_db_version_compat() -> bool:
    # FIXME: use this to verify, e.g. cache reload(), and prior to any SQL operation
    pg_result = psql("SELECT * FROM version")
    return __db_target_ntdb__ == pg_result.row["version"]


def get_pg_version(**kwargs):
    _ = kwargs

    pg_result = psql("SELECT * FROM version")
    rows = pg_result.rows
    for row in rows:
        row["created"] = row["created"].isoformat()

    return Success200Response(data={"message": pg_result.msg, "versions": rows})
