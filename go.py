from flask import Flask, render_template

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://localhost:5432/m2m'
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)


class Positions(db.Model):
    __tablename__ = 'positions'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String)
    lat = db.Column('lat', db.Integer)
    lng = db.Column('long', db.Integer)


@app.route("/")
def hello_world():
    positions = Positions.query.all()
    return render_template('positions.html', positions=positions)


# List devices and the last time they were heard from.
@app.route(u"/devices", methods=["GET"])
def list_devices():
    pass


# Devices will register and will be returned basic configuration data.
@app.route(u"/devices", methods=["POST"])
def register_device():
    pass


# Is the device still alive?
@app.route(u"/devices/<uuid>/heartbeat", methods=["POST"])
def register_heartbeat():
    pass

if __name__ == "__main__":
    app.run()
