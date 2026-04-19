from flask import request
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field, ValidationError
from werkzeug.exceptions import NotFound

from app.extensions import db as db_ext
from app.schemas.errors import ErrorResponse
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.utils.auth_decorators import require_jwt


users_bp = APIBlueprint(
	"users",
	__name__,
	url_prefix="/api/v1/users",
	abp_tags=[Tag(name="Users")],
	abp_security=[{"BearerAuth": []}],
)


class UsersQueryParams(BaseModel):
	page: int = Field(default=1, ge=1, description="Numero de pagina.", example=1)
	page_size: int = Field(default=10, ge=1, le=100, description="Registros por pagina (max. 100).", example=10)
	name: str | None = Field(default=None, description="Filtrar por nombre.", example="Alis")
	email: str | None = Field(default=None, description="Filtrar por correo.", example="usuario@gmail.com")
	order_by: str = Field(default="created_at", description="Campo por el que ordenar.", example="created_at")
	order_dir: str = Field(default="desc", pattern="^(asc|desc)$", description="Direccion del ordenamiento: 'asc' o 'desc'.", example="desc")


class UserPath(BaseModel):
	record_id: int = Field(..., description="ID del usuario.", example=1)


def get_db():
	"""Retorna la sesion de SQLAlchemy para usar en cada request."""
	return db_ext.session


@users_bp.post(
	"",
	summary="Crear un usuario",
	description="Crea un nuevo usuario.",
	responses={201: UserResponse, 400: ErrorResponse, 401: ErrorResponse, 422: ErrorResponse},
)
@require_jwt

def create_user(body: UserCreate):
	"""Crea un nuevo usuario."""
	try:
		payload = UserCreate.model_validate(request.get_json(silent=True) or {})
		result = UserService.create_record(get_db(), payload)
		return result.model_dump(mode="json"), 201
	except ValidationError as exc:
		return jsonify({"error": "VALIDATION_ERROR", "message": "Datos invalidos", "details": exc.errors()}), 400
	except ValueError as exc:
		return jsonify({"error": "BAD_REQUEST", "message": str(exc)}), 400
	except Exception:
		return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500


@users_bp.get(
	"",
	summary="Listar usuarios",
	description="Lista usuarios con paginacion, filtros y ordenamiento.",
	responses={200: UserListResponse, 400: ErrorResponse, 401: ErrorResponse},
)
@require_jwt

def list_users(query: UsersQueryParams):
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
		return result.model_dump(mode="json"), 200
	except ValueError as exc:
		return jsonify({"error": "BAD_REQUEST", "message": str(exc)}), 400
	except Exception:
		return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500


@users_bp.get(
	"/<int:record_id>",
	summary="Obtener usuario por ID",
	description="Retorna la informacion completa de un usuario.",
	responses={200: UserResponse, 401: ErrorResponse, 404: ErrorResponse},
)
@require_jwt

def get_user(path: UserPath):
	"""Obtiene un usuario por su identificador."""
	try:
		result = UserService.get_record(get_db(), path.record_id)
		return result.model_dump(mode="json"), 200
	except NotFound as exc:
		return jsonify({"error": "NOT_FOUND", "message": exc.description}), 404
	except Exception:
		return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500


@users_bp.put(
	"/<int:record_id>",
	summary="Actualizar usuario",
	description="Actualiza uno o mas campos del usuario.",
	responses={200: UserResponse, 400: ErrorResponse, 401: ErrorResponse, 404: ErrorResponse, 422: ErrorResponse},
)
@require_jwt

def update_user(path: UserPath, body: UserUpdate):
	"""Actualiza un usuario existente."""
	try:
		payload = UserUpdate.model_validate(request.get_json(silent=True) or {})
		result = UserService.update_record(get_db(), path.record_id, payload)
		return result.model_dump(mode="json"), 200
	except ValidationError as exc:
		return jsonify({"error": "VALIDATION_ERROR", "message": "Datos invalidos", "details": exc.errors()}), 400
	except NotFound as exc:
		return jsonify({"error": "NOT_FOUND", "message": exc.description}), 404
	except ValueError as exc:
		return jsonify({"error": "BAD_REQUEST", "message": str(exc)}), 400
	except Exception:
		return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500


@users_bp.delete(
	"/<int:record_id>",
	summary="Eliminar usuario",
	description="Elimina un usuario por su identificador.",
	responses={200: None, 401: ErrorResponse, 404: ErrorResponse},
)
@require_jwt

def delete_user(path: UserPath):
	"""Elimina un usuario por su identificador."""
	try:
		UserService.delete_record(get_db(), path.record_id)
		return {"deleted": True}, 200
	except NotFound as exc:
		return jsonify({"error": "NOT_FOUND", "message": exc.description}), 404
	except Exception:
		return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500
