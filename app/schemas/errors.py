
from typing import Any, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error específico"""

    field: str = Field(..., description="Campo que causó el error.", example="patient_name")
    message: str = Field(..., description="Descripción del error.", example="El nombre no puede estar vacío.")


class ErrorResponse(BaseModel):
   
    error: str = Field(..., description="Código o tipo de error.", example="VALIDATION_ERROR")
    message: str = Field(..., description="Descripción legible del error.", example="Los datos enviados no son válidos.")
    details: Optional[list[ErrorDetail]] = Field(
        default=None,
        description="Lista de errores por campo (solo en errores de validación 422).",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "Los datos enviados no son válidos.",
                "details": [
                    {"field": "patient_name", "message": "El nombre no puede estar vacío."},
                    {"field": "study_date", "message": "La fecha debe tener el formato YYYY-MM-DD."},
                ],
            }
        }
    }

class ErrorCodes:
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    CONFLICT = "CONFLICT"