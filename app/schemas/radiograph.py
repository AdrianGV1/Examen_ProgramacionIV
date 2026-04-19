
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

class RadiographCreate(BaseModel):
    """Datos que se necesitan para crear una nueva placa"""

    patient_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Nombre completo del paciente.",
        example="Alis Cordero Fonseca",
    )
    patient_id_number: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Número de identificación.",
        example="1-1034-0578",
    )
    clinical_reference: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Descripción o referencia clínica breve del estudio.",
        example="Radiografía de tórax. Sospecha de neumonía en lóbulo inferior derecho.",
    )
    study_date: date = Field(
        ...,
        description="Fecha en que se realizó el estudio (YYYY-MM-DD).",
        example="2026-04-10",
    )
    image_url: str | None = Field(
        default=None,
        description="URL pública de la imagen en Cloudinary (opcional).",
        example="https://res.cloudinary.com/demo/image/upload/v1234567890/radiograph_1.jpg",
    )
    image_public_id: str | None = Field(
        default=None,
        description="Public ID de Cloudinary para gestionar la imagen.",
        example="radiografias/radiograph_1",
    )
    image_is_private: bool = Field(
        default=False,
        description="Indica si la imagen está marcada como privada/oculta.",
        example=False,
    )
    image_hidden_at: datetime | None = Field(
        default=None,
        description="Fecha y hora en que la imagen fue ocultada.",
        example="2026-04-18T15:20:00",
    )

    @field_validator("patient_name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("El nombre del paciente no puede estar vacío.")
        return value.strip()

    @field_validator("patient_id_number")
    @classmethod
    def id_number_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("El número de identificación no puede estar vacío.")
        return value.strip()

    @field_validator("clinical_reference")
    @classmethod
    def reference_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("La referencia clínica no puede estar vacía.")
        return value.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_name": "Alis Cordero Fonseca",
                "patient_id_number": "1-1034-0578",
                "clinical_reference": "Radiografía de tórax. Sospecha de neumonía en lóbulo inferior derecho.",
                "study_date": "2026-04-10",
                "image_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/radiograph_1.jpg",
                "image_public_id": "radiografias/radiograph_1",
                "image_is_private": False,
                "image_hidden_at": None,
            }
        }
    }


class RadiographUpdate(BaseModel):

    patient_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=150,
        description="Nombre completo del paciente.",
        example="Alis Cordero Fonseca",
    )
    patient_id_number: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="Número de identificación o código de historia clínica.",
        example="1-1034-0578",
    )
    clinical_reference: Optional[str] = Field(
        default=None,
        min_length=5,
        max_length=500,
        description="Descripción o referencia clínica breve.",
        example="Seguimiento post-tratamiento. Mejora visible en lóbulo inferior.",
    )
    study_date: Optional[date] = Field(
        default=None,
        description="Fecha del estudio (YYYY-MM-DD).",
        example="2026-04-15",
    )
    image_url: Optional[str] = Field(
        default=None,
        description="URL pública de la imagen en Cloudinary.",
        example="https://res.cloudinary.com/demo/image/upload/v1234567890/radiograph_1.jpg",
    )
    image_public_id: Optional[str] = Field(
        default=None,
        description="Public ID de Cloudinary asociado a la imagen.",
        example="radiografias/radiograph_1",
    )
    image_is_private: Optional[bool] = Field(
        default=None,
        description="Marca la imagen como privada/oculta.",
        example=True,
    )
    image_hidden_at: Optional[datetime] = Field(
        default=None,
        description="Fecha y hora en que se ocultó la imagen.",
        example="2026-04-18T15:20:00",
    )

    @field_validator("patient_name")
    @classmethod
    def name_not_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError("El nombre del paciente no puede estar vacío.")
        return value.strip() if value else value

    model_config = {
        "json_schema_extra": {
            "example": {
                "clinical_reference": "Seguimiento post-tratamiento. Mejora visible en lóbulo inferior.",
                "study_date": "2026-04-15",
                "image_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/radiograph_1.jpg",
                "image_public_id": "radiografias/radiograph_1",
                "image_is_private": True,
                "image_hidden_at": "2026-04-18T15:20:00",
            }
        }
    }


class RadiographResponse(BaseModel):
    """Esto es lo que devuelve o retorna"""

    id: int = Field(..., description="ID único del registro.", example=1)
    patient_name: str = Field(..., description="Nombre completo del paciente.", example="Alis Cordero Fonseca")
    patient_id_number: str = Field(..., description="Número de identificación.", example="1-1034-0578")
    clinical_reference: str = Field(
        ...,
        description="Referencia clínica del estudio.",
        example="Radiografía de tórax. Sospecha de neumonía en lóbulo inferior derecho.",
    )
    study_date: date = Field(..., description="Fecha del estudio.", example="2026-04-10")
    image_url: str | None = Field(
        default=None,
        description="URL pública de la imagen en Cloudinary (CDN).",
        example="https://res.cloudinary.com/demo/image/upload/v1234567890/radiograph_1.jpg",
    )
    image_public_id: str | None = Field(
        default=None,
        description="Public ID de Cloudinary para la imagen.",
        example="radiografias/radiograph_1",
    )
    image_is_private: bool = Field(
        ...,
        description="Indica si la imagen está privada/oculta.",
        example=False,
    )
    image_hidden_at: datetime | None = Field(
        default=None,
        description="Fecha y hora en que la imagen fue ocultada.",
        example="2026-04-18T15:20:00",
    )
    created_at: datetime = Field(..., description="Fecha y hora de creación del registro.")
    updated_at: datetime = Field(..., description="Fecha y hora de la última actualización.")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "patient_name": "Alis Cordero Fonseca",
                "patient_id_number": "1-1034-0578",
                "clinical_reference": "Radiografía de tórax. Sospecha de neumonía en lóbulo inferior derecho.",
                "study_date": "2026-04-10",
                "image_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/radiograph_1.jpg",
                "image_public_id": "radiografias/radiograph_1",
                "image_is_private": False,
                "image_hidden_at": None,
                "created_at": "2026-04-14T10:30:00",
                "updated_at": "2026-04-14T10:30:00",
            }
        },
    }


class RadiographListResponse(BaseModel):
    """ Lista de placas"""

    items: list[RadiographResponse] = Field(..., description="Lista de registros en la página actual.")
    total: int = Field(..., description="Total de registros que coinciden con el filtro.", example=42)
    page: int = Field(..., description="Página actual (empieza en 1).", example=1)
    page_size: int = Field(..., description="Cantidad de registros por página.", example=10)
    pages: int = Field(..., description="Total de páginas disponibles.", example=5)

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "patient_name": "Alis Cordero Fonseca",
                        "patient_id_number": "1-1034-0578",
                        "clinical_reference": "Radiografía de tórax.",
                        "study_date": "2026-04-10",
                        "image_url": "https://res.cloudinary.com/demo/image/upload/v1234567890/radiograph_1.jpg",
                        "image_public_id": "radiografias/radiograph_1",
                        "image_is_private": False,
                        "image_hidden_at": None,
                        "created_at": "2026-04-14T10:30:00",
                        "updated_at": "2026-04-14T10:30:00",
                    }
                ],
                "total": 42,
                "page": 1,
                "page_size": 10,
                "pages": 5,
            }
        }
    }