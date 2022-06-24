from ntserv.server import app
from ntserv.settings import DEBUG, HOST, PORT

if __name__ == "__main__":
    print("[__main__] starting app...")
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
        auto_reload=DEBUG,
    )
