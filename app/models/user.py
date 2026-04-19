from datetime import datetime

from app.extensions import db


class User(db.Model):
	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	email = db.Column(db.String(255), nullable=False, unique=True, index=True)
	name = db.Column(db.String(150), nullable=False)
	picture = db.Column(db.String(500), nullable=True)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

	def __repr__(self) -> str:
		return f"<User id={self.id} email='{self.email}' name='{self.name}'>"
