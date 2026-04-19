"""
Servicio para gestionar usuarios en contexto de OAuth.
"""
from app.extensions import db
from app.models.user import User

class UserOAuthService:
	"""Maneja la creación y actualización de usuarios desde datos OAuth."""

	@staticmethod
	def get_or_create_user(email: str, name: str = None, picture: str = None) -> User:
		"""
		Obtiene un usuario existente o crea uno nuevo con datos OAuth.
		
		Args:
			email: Email del usuario (debe venir de Google validado)
			name: Nombre del usuario (opcional)
			picture: URL de foto de perfil (opcional)
			
		Returns:
			Usuario creado o actualizado
		"""
		# Buscar usuario existente por email
		user = User.query.filter_by(email=email).first()
		
		if user:
			# Actualizar nombre y foto si vienen nuevos
			if name:
				user.name = name
			if picture:
				user.picture = picture
			db.session.commit()
		else:
			# Crear nuevo usuario
			user = User(
				email=email,
				name=name or email.split("@")[0],
				picture=picture
			)
			db.session.add(user)
			db.session.commit()
		
		return user
