from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError
from werkzeug.exceptions import NotFound

from app.extensions import db as db_ext
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService


users_bp = Blueprint("users", __name__, url_prefix="/users")


def get_db():
	"""Retorna la sesion de SQLAlchemy para usar en cada request."""
	return db_ext.session


@users_bp.post("")
@jwt_required()
def create_user():
	"""Crea un nuevo usuario."""
	try:
		payload = UserCreate.model_validate(request.get_json(silent=True) or {})
		result = UserService.create_record(get_db(), payload)
		return jsonify(result.model_dump(mode="json")), 201
	except ValidationError as exc:
		return jsonify({"error": "VALIDATION_ERROR", "message": "Datos invalidos", "details": exc.errors()}), 400
	except ValueError as exc:
		return jsonify({"error": "BAD_REQUEST", "message": str(exc)}), 400
	except Exception:
		return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500


@users_bp.get("")
@jwt_required()
def list_users():
	"""Lista usuarios con paginacion, filtros y ordenamiento."""
	try:
		page = int(request.args.get("page", 1))
		page_size = int(request.args.get("page_size", 10))
		if page < 1:
			raise ValueError("page debe ser mayor o igual a 1")
		if page_size < 1 or page_size > 100:
			raise ValueError("page_size debe estar entre 1 y 100")

		name = request.args.get("name")
		email = request.args.get("email")
		order_by = request.args.get("order_by", "created_at")
		order_dir = request.args.get("order_dir", "desc").lower()
		if order_dir not in {"asc", "desc"}:
			raise ValueError("order_dir debe ser 'asc' o 'desc'")

		result = UserService.list_records(get_db(), page, page_size, name, email, order_by, order_dir)
		return jsonify(result.model_dump(mode="json")), 200
	except ValueError as exc:
		return jsonify({"error": "BAD_REQUEST", "message": str(exc)}), 400
	except Exception:
		return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500


@users_bp.get("/<int:record_id>")
@jwt_required()
def get_user(record_id: int):
	"""Obtiene un usuario por su identificador."""
	try:
		result = UserService.get_record(get_db(), record_id)
		return jsonify(result.model_dump(mode="json")), 200
	except NotFound as exc:
		return jsonify({"error": "NOT_FOUND", "message": exc.description}), 404
	except Exception:
		return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500


@users_bp.put("/<int:record_id>")
@jwt_required()
def update_user(record_id: int):
	"""Actualiza un usuario existente."""
	try:
		payload = UserUpdate.model_validate(request.get_json(silent=True) or {})
		result = UserService.update_record(get_db(), record_id, payload)
		return jsonify(result.model_dump(mode="json")), 200
	except ValidationError as exc:
		return jsonify({"error": "VALIDATION_ERROR", "message": "Datos invalidos", "details": exc.errors()}), 400
	except NotFound as exc:
		return jsonify({"error": "NOT_FOUND", "message": exc.description}), 404
	except ValueError as exc:
		return jsonify({"error": "BAD_REQUEST", "message": str(exc)}), 400
	except Exception:
		return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500


@users_bp.delete("/<int:record_id>")
@jwt_required()
def delete_user(record_id: int):
	"""Elimina un usuario por su identificador."""
	try:
		UserService.delete_record(get_db(), record_id)
		return jsonify({"deleted": True}), 200
	except NotFound as exc:
		return jsonify({"error": "NOT_FOUND", "message": exc.description}), 404
	except Exception:
		return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500
