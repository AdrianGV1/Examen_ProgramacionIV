
from flask_openapi3 import OpenAPI

from app.config import (
    SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS,
    SECRET_KEY,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
)
from app.config_swagger import API_INFO, SECURITY_SCHEMES


def create_app():
    app = OpenAPI(__name__, info=API_INFO, security_schemes=SECURITY_SCHEMES)

    # ========================
    # Configuración de Flask
    # ========================
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config["SECRET_KEY"] = SECRET_KEY

    # ========================
    # Configuración de JWT
    # ========================
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["JWT_ALGORITHM"] = JWT_ALGORITHM
    app.config["JWT_ACCESS_TOKEN_EXPIRES_MINUTES"] = JWT_ACCESS_TOKEN_EXPIRES_MINUTES

    # ========================
    # Configuración de Google OAuth (Flask-Dance)
    # ========================
    app.config["GOOGLE_CLIENT_ID"] = GOOGLE_CLIENT_ID
    app.config["GOOGLE_CLIENT_SECRET"] = GOOGLE_CLIENT_SECRET

    # ========================
    # Inicializar extensiones
    # ========================
    from app.extensions import db, migrate
    from app.models.user import User  # noqa: F401
    from app.models.radiograph import Radiograph  # noqa: F401

    db.init_app(app)
    migrate.init_app(app, db)

    # ========================
    # Registrar blueprints
    # ========================
    from app.routers.auth_router import auth_bp, google_bp
    from app.routers.records_router import records_bp
    from app.routers.upload_router import uploads_bp
    from app.routers.users import users_bp

    # Registrar auth blueprint en /auth
    app.register_api(auth_bp)
    app.register_blueprint(google_bp, url_prefix="/auth")
    app.register_api(records_bp)
    app.register_api(uploads_bp)
    app.register_api(users_bp)


    return app
