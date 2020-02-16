import os, sys
from traceback import format_tb

try:
    # edit your username below
    sys.path.append("/home/nutra/public_html/api");

    sys.path.insert(0, os.path.dirname(__file__))

    os.chdir("/home/nutra/public_html/api")
    from server import app

    # make the secret code a little better
    app.secret_key = 'secret'
    
    # start server
    #port = int(os.getenv("PORT", 20000))
    #if port == 81:
    #    port = 20000
    app.run(
    #    host="127.0.0.1", port=port, debug=True,
    #    host="127.0.0.1", debug=True,
    #    debug=True,
    )
except Exception as e:
    with open('/home/nutra/public_html/api/error.txt', 'w+') as f:
        f.write(repr(e) + '\n')
        f.write('\n'.join(format_tb(e.__traceback__)))
