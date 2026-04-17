"""
Decorador JWT para proteger endpoints.
Extrae el JWT del header Authorization, lo valida, e inyecta request.current_user.
"""
from functools import wraps
from flask import request, jsonify, g
import jwt
from app.services.jwt_service import JWTService
from app.models.user import User

def require_jwt(f):
	"""
	Decorador que protege un endpoint requiriendo JWT válido.
	
	Usage:
		@app.route('/protected')
		@require_jwt
		def protected_route():
			user = request.current_user
			return {"user_id": user.id, "email": user.email}
	"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		# Obtener header Authorization
		auth_header = request.headers.get("Authorization", "")
		
		if not auth_header:
			return jsonify({
				"error": "unauthorized",
				"message": "Missing Authorization header"
			}), 401
		
		# Validar formato: "Bearer <token>"
		parts = auth_header.split()
		if len(parts) != 2 or parts[0].lower() != "bearer":
			return jsonify({
				"error": "unauthorized",
				"message": "Invalid Authorization header format. Expected: 'Bearer <token>'"
			}), 401
		
		token = parts[1]
		
		try:
			# Decodificar y validar JWT
			payload = JWTService.decode_access_token(token)
			user_id = payload.get("sub")
			email = payload.get("email")

			try:
				user_id = int(user_id)
			except (TypeError, ValueError):
				return jsonify({
					"error": "unauthorized",
					"message": "Invalid token subject"
				}), 401
			
			# Obtener usuario de la BD
			user = User.query.filter_by(id=user_id, email=email).first()
			if not user:
				return jsonify({
					"error": "unauthorized",
					"message": "User not found"
				}), 401
			
			# Inyectar usuario en request context
			request.current_user = user
			g.current_user = user
			
			return f(*args, **kwargs)
		
		except jwt.ExpiredSignatureError:
			return jsonify({
				"error": "unauthorized",
				"message": "Token has expired"
			}), 401
		
		except jwt.InvalidTokenError as e:
			return jsonify({
				"error": "unauthorized",
				"message": f"Invalid token: {str(e)}"
			}), 401
		
		except Exception as e:
			return jsonify({
				"error": "unauthorized",
				"message": "Token validation failed"
			}), 401
	
	return decorated_function
