"""
Servicio de Autenticación con Google SSO y JWT
"""
from datetime import datetime, timedelta
from typing import Optional

import jwt
from flask_jwt_extended import create_access_token
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from werkzeug.exceptions import BadRequest, Unauthorized

from app import config
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserInfoResponse


class AuthServiceError(Exception):
	"""Excepción personalizada para errores de autenticación"""
	def __init__(self, message: str, status_code: int = 400):
		self.message = message
		self.status_code = status_code
		super().__init__(message)


class AuthService:
	"""Servicio de autenticación con Google SSO y JWT"""

	@staticmethod
	def validate_google_token(id_token_str: str) -> dict:
		"""
		Valida el ID token de Google.
		
		Args:
			id_token_str: Token ID recibido del frontend (Google OAuth)
			
		Returns:
			dict: Información del usuario desde Google (email, name, picture, etc.)
			
		Raises:
			AuthServiceError: Si el token no es válido
		"""
		if not id_token_str or not id_token_str.strip():
			raise AuthServiceError("ID token es requerido", 400)

		if not config.GOOGLE_CLIENT_ID:
			raise AuthServiceError(
				"Google Client ID no está configurado. Verifica variables de entorno.",
				500
			)

		try:
			# Valida el token con Google
			idinfo = google_id_token.verify_oauth2_token(
				id_token_str.strip(),
				google_requests.Request(),
				config.GOOGLE_CLIENT_ID
			)

			# Verifica que sea de Google
			if idinfo.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
				raise AuthServiceError("Token issuer inválido", 400)

			return idinfo

		except ValueError as exc:
			raise AuthServiceError("ID token inválido o expirado", 400) from exc
		except Exception as exc:
			raise AuthServiceError("Error validando token de Google", 500) from exc

	@staticmethod
	def get_or_create_user(db, google_data: dict) -> User:
		"""
		Obtiene o crea un usuario desde datos de Google.
		
		Args:
			db: Sesión de SQLAlchemy
			google_data: Datos devueltos por Google (contiene email, name, picture)
			
		Returns:
			User: Objeto usuario
		"""
		email = google_data.get("email")
		if not email:
			raise AuthServiceError("El token de Google debe contener email", 400)

		# Busca si el usuario existe
		user = db.query(User).filter(User.email == email).first()

		if user:
			# Actualiza datos del usuario (por si cambió nombre o foto)
			user.name = google_data.get("name", user.name)
			user.picture = google_data.get("picture", user.picture)
			db.commit()
			db.refresh(user)
			return user

		# Crea nuevo usuario
		user_data = {
			"email": email,
			"name": google_data.get("name", "Usuario"),
			"picture": google_data.get("picture"),
		}

		user = User(**user_data)
		db.add(user)
		db.commit()
		db.refresh(user)

		return user

	@staticmethod
	def generate_jwt(user_id: int) -> dict:
		"""
		Genera un JWT para el usuario.
		
		Args:
			user_id: ID del usuario
			
		Returns:
			dict: {"access_token": "...", "token_type": "bearer"}
		"""
		try:
			access_token = create_access_token(
				identity=user_id,
				expires_delta=timedelta(seconds=config.JWT_ACCESS_TOKEN_EXPIRES)
			)

			return {
				"access_token": access_token,
				"token_type": "bearer",
			}
		except Exception as exc:
			raise AuthServiceError("Error generando token JWT", 500) from exc

	@staticmethod
	def get_current_user(db, user_id: int) -> UserInfoResponse:
		"""
		Obtiene la información del usuario autenticado actual.
		
		Args:
			db: Sesión de SQLAlchemy
			user_id: ID del usuario (del JWT)
			
		Returns:
			UserInfoResponse: Información del usuario
			
		Raises:
			AuthServiceError: Si el usuario no existe
		"""
		user = UserRepository.get_by_id(db, user_id)

		if not user:
			raise AuthServiceError("Usuario no encontrado", 404)

		return UserInfoResponse.model_validate(user)


