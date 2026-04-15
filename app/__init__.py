
from flask_openapi3 import OpenAPI
from app.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY
from app.config_swagger import API_INFO, SECURITY_SCHEMES


def create_app():
    app = OpenAPI(__name__, info=API_INFO, security_schemes=SECURITY_SCHEMES)

    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config["SECRET_KEY"] = SECRET_KEY

    from app.extensions import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)

    return app