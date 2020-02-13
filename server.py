#!/usr/bin/env python3

import os

from ntserv.server import app

print("[__main__] bypassing gunicorn...")
port = int(os.getenv("PORT", 20000))
app.run(
    host="127.0.0.1", port=port, debug=True,
)
