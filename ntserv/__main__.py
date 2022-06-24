#!/usr/bin/env python3
import gunicorn.app.wsgiapp

from ntserv.server import app
from ntserv.settings import DEBUG, ENV, HOST, PORT

if __name__ == "__main__":
    if ENV == "local":
        print("[__main__] bypassing gunicorn...")
        app.run(
            host=HOST,
            port=PORT,
            debug=DEBUG,
            auto_reload=DEBUG,
        )
    else:
        # TODO: get this working
        gunicorn.app.wsgiapp.Application.run(app)
