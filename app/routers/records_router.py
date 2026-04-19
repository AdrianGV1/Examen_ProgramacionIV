"""
Router de Placas Radiográficas (Records).

Endpoints:
- POST   /records          - Crear un nuevo registro
- GET    /records          - Listar registros (paginación, filtros, ordenamiento)
- GET    /records/<id>     - Obtener un registro por ID
- PUT    /records/<id>     - Actualizar un registro
- DELETE /records/<id>     - Eliminar un registro
"""

from datetime import date

from flask import current_app, request
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field, ValidationError
from werkzeug.exceptions import NotFound

from app.extensions import db as db_ext
from app import config
from app.schemas.radiograph import RadiographCreate, RadiographUpdate, RadiographResponse, RadiographListResponse
from app.schemas.upload import SignedImageAccessResponse
from app.schemas.errors import ErrorResponse
from app.services.image_access_service import ImageAccessService
from app.services.radiograph_service import RadiographService
from app.services.upload_service import UploadService, UploadServiceError
from app.utils.auth_decorators import require_jwt


# ─── APIBlueprint ────────────────────────────────────────────────────────────────

records_bp = APIBlueprint(
    "records",
    __name__,
    url_prefix="/api/v1/records",
    abp_tags=[Tag(name="Radiographs")],
    abp_security=[{"BearerAuth": []}],
)

# ─── Query params schema (para documentar filtros en Swagger) ─────────────────

class RecordsQueryParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Número de página.", example=1)
    page_size: int = Field(default=10, ge=1, le=100, description="Registros por página (máx. 100).", example=10)
    patient_name: str | None = Field(default=None, description="Filtrar por nombre del paciente.", example="Carlos")
    patient_id_number: str | None = Field(default=None, description="Filtrar por número de identificación.", example="1-1234-5678")
    study_date_from: date | None = Field(default=None, description="Fecha de inicio del rango (YYYY-MM-DD).", example="2026-01-01")
    study_date_to: date | None = Field(default=None, description="Fecha fin del rango (YYYY-MM-DD).", example="2026-04-19")
    order_by: str = Field(default="created_at", description="Campo por el que ordenar.", example="created_at")
    order_dir: str = Field(default="desc", pattern="^(asc|desc)$", description="Dirección del ordenamiento: 'asc' o 'desc'.", example="desc")


class RecordPath(BaseModel):
    record_id: int = Field(..., description="ID del registro radiográfico.", example=1)


class SignedImageQueryParams(BaseModel):
    expires_minutes: int = Field(
        default=config.SIGNED_IMAGE_URL_EXPIRES_MINUTES,
        ge=1,
        le=60,
        description="Minutos de vigencia de la URL firmada (1-60).",
        example=10,
    )


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_db():
    """Retorna la sesión de SQLAlchemy para usar en cada request."""
    return db_ext.session


def _parse_iso_date(value: str | None, field_name: str):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} debe tener formato YYYY-MM-DD") from exc


# ─── Endpoints ────────────────────────────────────────────────────────────────

@records_bp.post(
    "",
    summary="Crear una nueva placa radiográfica",
    description=(
        "Crea un nuevo registro de placa radiográfica con los datos del paciente. "
        "Permite asociar metadata de Cloudinary (`image_public_id`) y visibilidad "
        "(`image_is_private`, `image_hidden_at`)."
    ),
    responses={
        201: RadiographResponse,
        400: ErrorResponse,
        401: ErrorResponse,
        422: ErrorResponse,
    },
)
@require_jwt
def create_record(body: RadiographCreate):
    """Crea un nuevo registro radiográfico."""
    try:
        payload = RadiographCreate.model_validate(request.get_json(silent=True) or {})
        result = RadiographService.create_record(get_db(), payload)
        return result.model_dump(mode="json"), 201
    except ValidationError as exc:
        return {"error": "VALIDATION_ERROR", "message": "Datos inválidos", "details": exc.errors()}, 400
    except ValueError as exc:
        return {"error": "BAD_REQUEST", "message": str(exc)}, 400
    except UploadServiceError as exc:
        return {"error": exc.code, "message": exc.message}, exc.status_code
    except Exception:
        return {"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}, 500


@records_bp.get(
    "",
    summary="Listar placas radiográficas",
    description=(
        "Retorna una lista paginada de registros. "
        "Soporta filtros por nombre, número de identificación y rango de fechas. "
        "También permite ordenar por cualquier campo."
    ),
    responses={
        200: RadiographListResponse,
        400: ErrorResponse,
        401: ErrorResponse,
    },
)
@require_jwt
def list_records(query: RecordsQueryParams):
    """Lista registros radiográficos con paginación, filtros y ordenamiento."""
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
            get_db(), page, page_size,
            patient_name, patient_id_number,
            study_date_from, study_date_to,
            order_by, order_dir,
        )
        return result.model_dump(mode="json"), 200
    except ValueError as exc:
        return {"error": "BAD_REQUEST", "message": str(exc)}, 400
    except Exception:
        return {"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}, 500


@records_bp.get(
    "/<int:record_id>",
    summary="Obtener una placa radiográfica por ID",
    description="Retorna el detalle completo de un registro específico, incluyendo la URL de la imagen en Cloudinary.",
    responses={
        200: RadiographResponse,
        401: ErrorResponse,
        404: ErrorResponse,
    },
)
@require_jwt
def get_record(path: RecordPath):
    """Obtiene un registro radiográfico por su identificador."""
    try:
        result = RadiographService.get_record(get_db(), path.record_id)
        return result.model_dump(mode="json"), 200
    except NotFound as exc:
        return {"error": "NOT_FOUND", "message": exc.description}, 404
    except Exception:
        return {"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}, 500


@records_bp.put(
    "/<int:record_id>",
    summary="Actualizar una placa radiográfica",
    description=(
        "Actualiza uno o más campos del registro. "
        "Solo es necesario enviar los campos que se desean modificar, incluyendo "
        "metadata de imagen y estado de privacidad."
    ),
    responses={
        200: RadiographResponse,
        400: ErrorResponse,
        401: ErrorResponse,
        404: ErrorResponse,
        422: ErrorResponse,
    },
)
@require_jwt
def update_record(path: RecordPath, body: RadiographUpdate):
    """Actualiza parcialmente un registro radiográfico."""
    try:
        payload = RadiographUpdate.model_validate(request.get_json(silent=True) or {})
        result = RadiographService.update_record(get_db(), path.record_id, payload)
        return result.model_dump(mode="json"), 200
    except ValidationError as exc:
        return {"error": "VALIDATION_ERROR", "message": "Datos inválidos", "details": exc.errors()}, 400
    except NotFound as exc:
        return {"error": "NOT_FOUND", "message": exc.description}, 404
    except ValueError as exc:
        return {"error": "BAD_REQUEST", "message": str(exc)}, 400
    except UploadServiceError as exc:
        return {"error": exc.code, "message": exc.message}, exc.status_code
    except Exception as exc:
        current_app.logger.exception("update_record failed: %s", exc)
        return {"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}, 500


@records_bp.delete(
    "/<int:record_id>",
    summary="Eliminar una placa radiográfica",
    description="Elimina permanentemente un registro radiográfico y su referencia de imagen.",
    responses={
        200: None,
        401: ErrorResponse,
        404: ErrorResponse,
    },
)
@require_jwt
def delete_record(path: RecordPath):
    """Elimina un registro radiográfico por su identificador."""
    try:
        RadiographService.delete_record(get_db(), path.record_id)
        return {"deleted": True}, 200
    except NotFound as exc:
        return {"error": "NOT_FOUND", "message": exc.description}, 404
    except Exception:
        return {"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}, 500


@records_bp.get(
    "/<int:record_id>/signed-image-url",
    summary="Obtener URL firmada temporal para imagen oculta",
    description=(
        "Genera una URL firmada temporal y un token adicional por usuario para acceder "
        "a una imagen marcada como privada."
    ),
    responses={
        200: SignedImageAccessResponse,
        400: ErrorResponse,
        401: ErrorResponse,
        404: ErrorResponse,
        502: ErrorResponse,
    },
)
@require_jwt
def get_signed_image_url(path: RecordPath, query: SignedImageQueryParams):
    try:
        record = RadiographService.get_record(get_db(), path.record_id)

        if not record.image_is_private:
            return {
                "error": "BAD_REQUEST",
                "message": "La imagen no está oculta; no requiere URL firmada",
            }, 400

        if not record.image_public_id:
            return {
                "error": "BAD_REQUEST",
                "message": "El registro no tiene image_public_id para firmar acceso",
            }, 400

        expires_minutes = int(request.args.get("expires_minutes", config.SIGNED_IMAGE_URL_EXPIRES_MINUTES))
        if expires_minutes < 1 or expires_minutes > 60:
            raise ValueError("expires_minutes debe estar entre 1 y 60")

        current_user = request.current_user
        token_data = ImageAccessService.generate_user_access_token(
            user_id=current_user.id,
            record_id=record.id,
            public_id=record.image_public_id,
            expires_minutes=expires_minutes,
        )

        signed_data = UploadService.generate_temporary_signed_url(
            public_id=record.image_public_id,
            expires_minutes=expires_minutes,
            user_access_token=token_data["token"],
            image_url=record.image_url,
        )

        payload = SignedImageAccessResponse(
            record_id=record.id,
            signed_url=signed_data["signed_url"],
            access_token=token_data["token"],
            expires_at=signed_data["expires_at"],
            expires_in_seconds=signed_data["expires_in_seconds"],
        )
        return payload.model_dump(mode="json"), 200
    except ValueError as exc:
        return {"error": "BAD_REQUEST", "message": str(exc)}, 400
    except NotFound as exc:
        return {"error": "NOT_FOUND", "message": exc.description}, 404
    except UploadServiceError as exc:
        return {"error": exc.code, "message": exc.message}, exc.status_code
    except Exception:
        return {"error": "INTERNAL_ERROR", "message": "Error interno del servidor"}, 500