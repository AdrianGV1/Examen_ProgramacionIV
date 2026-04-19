from flask import redirect, url_for, request
from flask_openapi3 import APIBlueprint
from flask_dance.contrib.google import google, make_google_blueprint

from app.extensions import db
from app.services.auth_service import AuthService
from app.utils.auth_decorators import require_jwt
from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from app.schemas import TokenResponse, UserInfoResponse, ErrorResponse
from flask_openapi3 import APIBlueprint, Tag

auth_bp = APIBlueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    abp_tags=[Tag(name="Auth")],
)

def create_google_blueprint():
    return make_google_blueprint(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scope=["openid", "email", "profile"],
        redirect_to="auth.callback",
    )

google_bp = create_google_blueprint()

@auth_bp.get("/login", summary="Iniciar sesión con Google",
    description="Redirige al flujo de autenticación de Google OAuth.",
    responses={302: None})
def login():
    return redirect(url_for("google.login"))

@auth_bp.get("/callback", summary="Callback de Google OAuth",
    description="Google redirige aquí tras autorizar. Genera y retorna el JWT.",
    responses={200: TokenResponse, 401: ErrorResponse, 500: ErrorResponse})
def callback():
    if not google.authorized:
        return {"error": "UNAUTHORIZED", "message": "No autorizado con Google."}, 401
    try:
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            raise Exception("No se pudo obtener información del usuario desde Google.")
        google_user = resp.json()
        if not google_user.get("verified_email"):
            return {"error": "UNAUTHORIZED", "message": "Email no verificado por Google."}, 401
        user = AuthService.get_or_create_user(
            db.session,
            {
                "email": google_user.get("email"),
                "name": google_user.get("name"),
                "picture": google_user.get("picture"),
            },
        )
        token_data = AuthService.generate_jwt(user.id, user.email)
        return token_data, 200
    except Exception as e:
        return {"error": "AUTH_ERROR", "message": str(e)}, 500

@auth_bp.get("/me", summary="Obtener usuario autenticado",
    description="Retorna la información del usuario dueño del JWT.",
    responses={200: UserInfoResponse, 401: ErrorResponse},
    security=[{"BearerAuth": []}])
@require_jwt
def get_current_user():
    user = request.current_user
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
    }, 200