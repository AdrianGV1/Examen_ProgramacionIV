
from flask_openapi3 import OpenAPI
from app.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY
from app.config_swagger import API_INFO, SECURITY_SCHEMES


def create_app():
    app = OpenAPI(__name__, info=API_INFO, security_schemes=SECURITY_SCHEMES)

    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config["SECRET_KEY"] = SECRET_KEY

    from app.extensions import db, migrate
    from app.models.user import User  # noqa: F401
    from app.models.radiograph import Radiograph  # noqa: F401

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routers.records import records_bp
    from app.routers.upload_router import uploads_bp
    from app.routers.users import users_bp
    app.register_blueprint(records_bp, url_prefix="/api/v1")
    app.register_api(uploads_bp, url_prefix="/api/v1")
    app.register_blueprint(users_bp, url_prefix="/api/v1")

    return app