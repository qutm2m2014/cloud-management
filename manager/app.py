# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from datastore import db
from extensions import socketio
import routes
import messagebusctl

DEFAULT_BLUEPRINTS = [routes.api]


def configure_extensions(app):
    db.init_app(app)
    socketio.init_app(app)


def configure_blueprints(app):
    for bp in DEFAULT_BLUEPRINTS:
        app.register_blueprint(bp)


def configure_error_handlers(app):

    @app.errorhandler(403)
    def not_allowed_error(errorhandlerror):
        return jsonify(error='Sorry, not allowed!'), 403

    @app.errorhandler(404)
    def malformed_request_error(errorhandlerror):
        return jsonify(error="Sorry, we don't understand!"), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify(error='Sorry, not found!'), 404

def create_app():
    app = Flask(__name__, static_url_path="/app", static_folder="static")
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://localhost:5432/m2m'
    app.config["SQLALCHEMY_ECHO"] = False
    configure_blueprints(app)
    configure_extensions(app)
    configure_error_handlers(app)
    with app.app_context():
        messagebusctl.run()

    @app.route('/app')
    def root():
        return app.send_static_file('index.html')

    return app

if __name__ == "__main__":
    create_app().run()
