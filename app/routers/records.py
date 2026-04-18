from datetime import date

from flask import Blueprint, jsonify, request
from app.utils.auth_decorators import require_jwt
from pydantic import ValidationError
from werkzeug.exceptions import NotFound

from app.extensions import db as db_ext
from app.schemas.radiograph import RadiographCreate, RadiographUpdate
from app.services.radiograph_service import RadiographService


records_bp = Blueprint("records", __name__, url_prefix="/records")


def get_db():
    """Retorna la sesion de SQLAlchemy para usar en cada request."""
    return db_ext.session


def _parse_iso_date(value: str | None, field_name: str):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} debe tener formato YYYY-MM-DD") from exc


@records_bp.post("")
@require_jwt
def create_record():
    """Crea un nuevo registro radiografico."""
    try:
        payload = RadiographCreate.model_validate(request.get_json(silent=True) or {})
        result = RadiographService.create_record(get_db(), payload)
        return jsonify(result.model_dump(mode="json")), 201
    except ValidationError as exc:
        return jsonify({"error": "VALIDATION_ERROR", "message": "Datos invalidos", "details": exc.errors()}), 400
    except ValueError as exc:
        return jsonify({"error": "BAD_REQUEST", "message": str(exc)}), 400
    except Exception:
        return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500


@records_bp.get("")
@require_jwt
def list_records():
    """Lista registros radiograficos con paginacion, filtros y ordenamiento."""
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))
        if page < 1:
            raise ValueError("page debe ser mayor o igual a 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size debe estar entre 1 y 100")

        patient_name = request.args.get("patient_name")
        patient_id_number = request.args.get("patient_id_number")
        study_date_from = _parse_iso_date(request.args.get("study_date_from"), "study_date_from")
        study_date_to = _parse_iso_date(request.args.get("study_date_to"), "study_date_to")

        order_by = request.args.get("order_by", "created_at")
        order_dir = request.args.get("order_dir", "desc").lower()
        if order_dir not in {"asc", "desc"}:
            raise ValueError("order_dir debe ser 'asc' o 'desc'")

        result = RadiographService.list_records(
            get_db(),
            page,
            page_size,
            patient_name,
            patient_id_number,
            study_date_from,
            study_date_to,
            order_by,
            order_dir,
        )
        return jsonify(result.model_dump(mode="json")), 200
    except ValueError as exc:
        return jsonify({"error": "BAD_REQUEST", "message": str(exc)}), 400
    except Exception:
        return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500


@records_bp.get("/<int:record_id>")
@require_jwt
def get_record(record_id: int):
    """Obtiene un registro radiografico por su identificador."""
    try:
        result = RadiographService.get_record(get_db(), record_id)
        return jsonify(result.model_dump(mode="json")), 200
    except NotFound as exc:
        return jsonify({"error": "NOT_FOUND", "message": exc.description}), 404
    except Exception:
        return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500


@records_bp.put("/<int:record_id>")
@require_jwt
def update_record(record_id: int):
    """Actualiza parcialmente un registro radiografico."""
    try:
        payload = RadiographUpdate.model_validate(request.get_json(silent=True) or {})
        result = RadiographService.update_record(get_db(), record_id, payload)
        return jsonify(result.model_dump(mode="json")), 200
    except ValidationError as exc:
        return jsonify({"error": "VALIDATION_ERROR", "message": "Datos invalidos", "details": exc.errors()}), 400
    except NotFound as exc:
        return jsonify({"error": "NOT_FOUND", "message": exc.description}), 404
    except ValueError as exc:
        return jsonify({"error": "BAD_REQUEST", "message": str(exc)}), 400
    except Exception:
        return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500


@records_bp.delete("/<int:record_id>")
@require_jwt
def delete_record(record_id: int):
    """Elimina un registro radiografico por su identificador."""
    try:
        RadiographService.delete_record(get_db(), record_id)
        return jsonify({"deleted": True}), 200
    except NotFound as exc:
        return jsonify({"error": "NOT_FOUND", "message": exc.description}), 404
    except Exception:
        return jsonify({"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}), 500
