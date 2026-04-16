from pydantic import BaseModel, Field


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
