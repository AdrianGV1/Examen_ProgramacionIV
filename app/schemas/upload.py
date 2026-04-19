from pydantic import BaseModel, Field
from datetime import datetime


class UploadResponse(BaseModel):
    """Respuesta de una carga exitosa a Cloudinary."""

    url: str = Field(
        ...,
        description="URL publica CDN de la imagen subida.",
    )
    public_id: str = Field(
        ...,
        description="Identificador unico del recurso en Cloudinary.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://res.cloudinary.com/tu-cloud/image/upload/v1710000000/radiografias/abc123.jpg",
                "public_id": "radiografias/abc123",
            }
        }
    }


class UploadDeleteResponse(BaseModel):
    """Respuesta para eliminacion de imagen en Cloudinary."""

    deleted: bool = Field(..., description="Indica si la imagen fue eliminada.")
    public_id: str = Field(..., description="Public ID eliminado.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "deleted": True,
                "public_id": "radiografias/abc123",
            }
        }
    }


class SignedImageAccessResponse(BaseModel):
    """Respuesta para acceso temporal a imágenes ocultas."""

    record_id: int = Field(..., description="ID del registro radiográfico.")
    signed_url: str = Field(..., description="URL firmada temporal para acceder a la imagen.")
    access_token: str = Field(..., description="Token adicional que identifica al usuario solicitante.")
    expires_at: datetime = Field(..., description="Fecha/hora UTC de expiración del acceso.")
    expires_in_seconds: int = Field(..., description="Segundos restantes de validez del acceso.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "record_id": 12,
                "signed_url": "https://api.cloudinary.com/v1_1/demo/download?...&user_token=...",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "expires_at": "2026-04-19T21:10:00Z",
                "expires_in_seconds": 600,
            }
        }
    }
