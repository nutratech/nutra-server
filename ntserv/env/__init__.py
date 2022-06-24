import getpass
import os
from datetime import timedelta

from dotenv import load_dotenv

# TODO: prefix these all with NTSERV_

# Read in .env file if it exists locally, else look to env vars
load_dotenv(verbose=True)

# Log level
LOG_LEVEL = int(os.getenv("NTSERV_LOG_LEVEL", str(10)))

# USPS API key
USPS_API_KEY = os.getenv("USPS_API_KEY")

# Email creds
PROD_EMAIL = os.getenv("PROD_EMAIL")
PROD_EMAIL_PASS = os.getenv("PROD_EMAIL_PASS")

# Server host
SERVER_PORT = os.getenv("PORT", str(20000))
ON_REMOTE = int(os.getenv("ON_REMOTE", str(0)))
# TODO: static domain
SERVER_HOST = (
    "https://vps76.heliohost.us" if ON_REMOTE else f"http://localhost:{SERVER_PORT}"
)
WEB_HOST = (
    "https://nutra-web.herokuapp.com"
    if ON_REMOTE
    else f"http://localhost:{SERVER_PORT}"
)

# PostgreSQL
PSQL_DATABASE = os.getenv("PSQL_DB_NAME", "nt")
PSQL_SCHEMA = os.getenv("PSQL_SCHEMA_NAME", "nt")

PSQL_USER = os.getenv("PSQL_USER", getpass.getuser())
PSQL_PASSWORD = os.getenv("PSQL_PASSWORD", "password")

PSQL_HOST = os.getenv("PSQL_HOST", "localhost")

# Server config
JWT_SECRET = os.getenv("JWT_SECRET", "secret123")
PROXY_SECRET = os.getenv("PROXY_SECRET", "secret123")

ENV = os.environ.get("ENV", "prod")
PORT = int(os.getenv("PORT", str(20000)))
HOST = os.getenv("HOST", "127.0.0.1")

DEBUG = bool(ENV == "local")

DEFAULT_WORKERS = 1 if DEBUG else 2
WORKERS = int(os.getenv("WORKERS", str(DEFAULT_WORKERS)))

# Other
TOKEN_EXPIRY = timedelta(weeks=520)
