import os, sys
from traceback import format_tb

try:
    # edit your username below
    sys.path.append("/home/nutra/public_html/api");

    sys.path.insert(0, os.path.dirname(__file__))
    from server import app as application

    # make the secret code a little better
    application.secret_key = 'secret'
except Exception as e:
    with open('error.txt', 'w+') as f:
        f.write(repr(e) + '\n')
        f.write('\n'.join(format_tb(e.__traceback__)))
