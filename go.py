from flask import Flask

app = Flask(__name__)
app.debug = True


@app.route(u"/")
def hello_world():
    return "Hello World"


@app.route(u"/devices")
def list_devices():
    pass


@app.route(u"/heartbeat", methods=["POST"])
def register_heartbeat():
    pass


if __name__ == "__main__":
    app.run()
