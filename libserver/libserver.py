import time
import datetime
import traceback


def Request(func, req):
    """ Makes a request and handles global exceptions, always returning a `Response()` """
    try:
        return func(request=req)
    except Exception as e:
        # Return error message
        stack_msg = f'{repr(e)}\n\n{traceback.format_tb(e.__traceback__)}'
        return Response(data={'error': 'General server error', 'stack': stack_msg}, code=500)


def Response(data={}, code=200, status='OK'):
    """ Creates a response object for the client """

    return {
        "program": 'nutra-server',
        "version": '0.0.1',
        "release": 1,
        "datetime": datetime.datetime.fromtimestamp(time.time()).strftime('%c'),
        "timestamp": int(time.time() * 1000),
        "status": status if code < 400 else 'Failure',
        "code": code,
        "data": data,
    }, code


def Text(text=None):
    return text
