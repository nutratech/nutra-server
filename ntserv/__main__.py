# -*- coding: utf-8 -*-
"""
Created on Fri 24 Jun 2022 03:24:38 PM EDT

@author: shane
"""

from ntserv.env import DEBUG, HOST, PORT, WORKERS
from ntserv.routes import app

if __name__ == "__main__":
    print("[__main__] starting app...")
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
        auto_reload=DEBUG,
        workers=WORKERS,
    )
