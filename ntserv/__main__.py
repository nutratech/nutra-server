#!/usr/bin/env python3

import os

import gunicorn.app.wsgiapp

from ntserv.server import app

ENV = os.environ.get("ENV", "local")
PORT = int(os.getenv("PORT", "20000"))
HOST = os.getenv("HOST", "127.0.0.1")

if __name__ == "__main__":
    if ENV == "local":
        print("[__main__] bypassing gunicorn...")
        app.run(
            host=HOST,
            port=PORT,
            debug=True,
            use_reloader=False,
            threaded=True,
        )
    else:
        # TODO: get this working
        gunicorn.app.wsgiapp.Application.run(app)
