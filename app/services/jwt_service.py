"""
Servicio JWT para generación y validación de tokens.
Usa PyJWT para crear JWTs seguros con expiración.
"""
import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app

class JWTService:
	"""Maneja la generación y validación de JWT tokens."""

	@staticmethod
	def generate_access_token(user_id: int, email: str) -> dict:
		"""
		Genera un token JWT con claims del usuario.
		
		Args:
			user_id: ID del usuario
			email: Email del usuario
			
		Returns:
			dict con access_token, token_type, expires_in
		"""
		now = datetime.now(timezone.utc)
		expires_minutes = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 60)
		expires_at = now + timedelta(minutes=expires_minutes)
		
		payload = {
			"sub": str(user_id),  # subject must be a string per JWT spec
			"email": email,
			"iat": now,  # issued at
			"exp": expires_at,  # expiration
			"type": "access"
		}
		
		token = jwt.encode(
			payload,
			current_app.config["JWT_SECRET_KEY"],
			algorithm=current_app.config.get("JWT_ALGORITHM", "HS256")
		)
		
		return {
			"access_token": token,
			"token_type": "Bearer",
			"expires_in": int(expires_minutes * 60)  # en segundos
		}

	@staticmethod
	def decode_access_token(token: str) -> dict:
		"""
		Decodifica y valida un JWT token.
		
		Args:
			token: Token JWT
			
		Returns:
			dict con claims del token (sub, email, etc)
			
		Raises:
			jwt.DecodeError: Si el token es inválido
			jwt.ExpiredSignatureError: Si el token expiró
		"""
		try:
			payload = jwt.decode(
				token,
				current_app.config["JWT_SECRET_KEY"],
				algorithms=[current_app.config.get("JWT_ALGORITHM", "HS256")]
			)
			
			# Validar que sea un token de acceso
			if payload.get("type") != "access":
				raise jwt.InvalidTokenError("Token type is not 'access'")
			
			return payload
			
		except jwt.ExpiredSignatureError:
			raise jwt.ExpiredSignatureError("Token has expired")
		except jwt.InvalidTokenError as e:
			raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")
