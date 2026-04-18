"""
Router de Autenticación con Google OAuth + JWT.

Endpoints:
- GET /auth/login - Inicia login con Google
- GET /auth/callback - Callback después de autorizar en Google
- GET /auth/me - Información del usuario autenticado (requiere JWT)
"""
from flask import Blueprint, redirect, url_for, jsonify, request
from flask_dance.contrib.google import google, make_google_blueprint
from app.extensions import db
from app.services.auth_service import AuthService
from app.utils.auth_decorators import require_jwt
from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

# Crear blueprint de autenticación
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Configurar Flask-Dance para Google OAuth
def create_google_blueprint():
	"""Crea y retorna el blueprint de Google OAuth."""
	return make_google_blueprint(
		client_id=GOOGLE_CLIENT_ID,
		client_secret=GOOGLE_CLIENT_SECRET,
		scope=["openid", "email", "profile"],
		redirect_to="auth.callback"
	)

google_bp = create_google_blueprint()

@auth_bp.route("/login")
def login():
	"""Inicia el flujo de login con Google."""
	return redirect(url_for("google.login"))

@auth_bp.route("/callback")
def callback():
	"""
	Callback después de que Google autoriza.
	Obtiene datos del usuario, crea/actualiza en BD, genera JWT.
	"""
	# Verificar que se autenticó correctamente
	if not google.authorized:
		return jsonify({
			"error": "unauthorized",
			"message": "Not authorized with Google"
		}), 401
	
	try:
		# Obtener información del usuario desde Google
		resp = google.get("/oauth2/v2/userinfo")
		if not resp.ok:
			raise Exception("Failed to fetch user info from Google")
		
		google_user = resp.json()
		email = google_user.get("email")
		name = google_user.get("name")
		picture = google_user.get("picture")
		
		# Validar que el email esté verificado
		if not google_user.get("verified_email"):
			return jsonify({
				"error": "unauthorized",
				"message": "Email not verified by Google"
			}), 401
		
		# Crear o actualizar usuario (servicio de auth)
		user = AuthService.get_or_create_user(
			db.session,
			{
				"email": email,
				"name": name,
				"picture": picture,
			},
		)

		# Generar JWT con servicio centralizado
		token_data = AuthService.generate_jwt(user.id, user.email)
		
		return jsonify(token_data), 200
	
	except Exception as e:
		return jsonify({
			"error": "auth_error",
			"message": str(e)
		}), 500

@auth_bp.route("/me")
@require_jwt
def get_current_user():
	"""
	Obtiene información del usuario autenticado.
	Requiere JWT válido en header Authorization.
	"""
	user = request.current_user
	return jsonify({
		"id": user.id,
		"email": user.email,
		"name": user.name,
		"picture": user.picture
	}), 200
