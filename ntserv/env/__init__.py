import getpass
import os
from datetime import timedelta

from dotenv import load_dotenv

# TODO: prefix these all with NTSERV_

# Read in .env file if it exists locally, else look to env vars
load_dotenv(verbose=True)

# Log level
LOG_LEVEL = int(os.getenv("NTSERV_LOG_LEVEL", str(10)))

# Server config
JWT_SECRET = os.getenv("NTSERV_JWT_SECRET", "secret123")
PROXY_SECRET = os.getenv("NTSERV_PROXY_SECRET", "secret123")

ENV = os.environ.get("NTSERV_ENV", "prod")
PORT = int(os.getenv("NTSERV_PORT", str(20000)))
HOST = os.getenv("NTSERV_HOST", "127.0.0.1")

DEBUG = bool(ENV == "local")

DEFAULT_WORKERS = 1 if DEBUG else 2
WORKERS = int(os.getenv("NTSERV_N_WORKERS", str(DEFAULT_WORKERS)))

# Server host
SERVER_PORT = os.getenv("NTSERV_PORT", str(20000))
# TODO: static domain
SERVER_HOST = (
    "https://vps76.heliohost.us" if ENV == "local" else f"http://{HOST}:{SERVER_PORT}"
)
WEB_HOST = (
    "https://nutra-web.herokuapp.com"
    if ENV == "local"
    else f"http://localhost:{SERVER_PORT}"
)

# PostgreSQL
PSQL_DATABASE = os.getenv("NTSERV_PSQL_DB_NAME", "nt")
PSQL_SCHEMA = os.getenv("NTSERV_PSQL_SCHEMA_NAME", "nt")

PSQL_USER = os.getenv("NTSERV_PSQL_USER", getpass.getuser())
PSQL_PASSWORD = os.getenv("NTSERV_PSQL_PASSWORD", "password")

PSQL_HOST = os.getenv("NTSERV_PSQL_HOST", "localhost")

# Email creds
PROD_EMAIL = os.getenv("NTSERV_PROD_EMAIL")
PROD_EMAIL_PASS = os.getenv("NTSERV_PROD_EMAIL_PASS")

# Other configurations
TOKEN_EXPIRY = timedelta(weeks=520)
