import os


def heroku():
    try:
        return (
            os.environ["HEROKU_RELEASE_VERSION"],
            os.environ["HEROKU_SLUG_COMMIT"][:9],
            os.environ["HEROKU_RELEASE_CREATED_AT"],
        )
    except KeyError as err:
        print(repr(err))
        return None, None, None
