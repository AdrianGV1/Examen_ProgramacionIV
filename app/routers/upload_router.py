from flask import jsonify, request
from flask_openapi3 import APIBlueprint
from app.utils.auth_decorators import require_jwt

from app.config_swagger import TAG_UPLOADS
from app.schemas.errors import ErrorCodes
from app.schemas.upload import UploadResponse, UploadDeleteResponse
from app.services.upload_service import UploadService, UploadServiceError


uploads_bp = APIBlueprint("uploads", __name__, url_prefix="/api/v1/uploads")


@uploads_bp.post(
    "",
    responses={"201": UploadResponse},
    summary="Subir imagen a Cloudinary",
    description="Sube una imagen radiografica a Cloudinary",
    tags=[TAG_UPLOADS],
)
@require_jwt
def upload_image():
    """Sube una imagen radiografica a Cloudinary.

    Request:
    - Content-Type: multipart/form-data
    - Campo requerido: file

    Validaciones:
    - Tipo de archivo permitido: jpg, jpeg, png, webp
    - Tamano maximo configurable via UPLOAD_MAX_FILE_SIZE_MB
    """
    try:
        file = request.files.get("file")
        if file is None:
            return (
                jsonify(
                    {
                        "error": ErrorCodes.VALIDATION_ERROR,
                        "message": "Debe enviar el campo 'file' en multipart/form-data",
                    }
                ),
                400,
            )

        result = UploadService.upload_image(file)
        return jsonify(result.model_dump(mode="json")), 201
    except UploadServiceError as exc:
        return jsonify({"error": exc.code, "message": exc.message}), exc.status_code
    except Exception:
        return (
            jsonify(
                {
                    "error": ErrorCodes.INTERNAL_ERROR,
                    "message": "Error interno del servidor",
                }
            ),
            500,
        )


@uploads_bp.delete(
    "/<path:public_id>",
    responses={"200": UploadDeleteResponse},
    summary="Eliminar imagen de Cloudinary",
    description="Elimina una imagen en Cloudinary por public_id",
    tags=[TAG_UPLOADS],
)
@require_jwt
def delete_image(public_id: str | None = None):
    """Elimina una imagen en Cloudinary por public_id."""
    try:
        # flask-openapi3 puede no pasar public_id como argumento posicional.
        # En ese caso, lo tomamos desde view_args del request.
        if public_id is None:
            public_id = (request.view_args or {}).get("public_id")
        if not public_id:
            return jsonify({"error": ErrorCodes.VALIDATION_ERROR, "message": "public_id es requerido"}), 400

        deleted = UploadService.delete_image(public_id)
        if not deleted:
            return jsonify({"error": ErrorCodes.NOT_FOUND, "message": "Imagen no encontrada en Cloudinary"}), 404

        payload = UploadDeleteResponse(deleted=True, public_id=public_id)
        return jsonify(payload.model_dump(mode="json")), 200
    except UploadServiceError as exc:
        return jsonify({"error": exc.code, "message": exc.message}), exc.status_code
    except Exception:
        return (
            jsonify(
                {
                    "error": ErrorCodes.INTERNAL_ERROR,
                    "message": "Error interno del servidor",
                }
            ),
            500,
        )
