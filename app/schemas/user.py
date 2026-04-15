
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Datos para crear un usuario."""

    email: EmailStr = Field(..., description="Correo del usuario.", example="usuario@gmail.com")
    name: str = Field(..., min_length=2, max_length=150, description="Nombre completo.", example="Alis Ureña")
    picture: str | None = Field(
        default=None,
        max_length=500,
        description="URL de foto de perfil.",
        example="https://lh3.googleusercontent.com/...",
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("El nombre no puede estar vacío.")
        return value.strip()

    @field_validator("picture")
    @classmethod
    def picture_strip_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        return cleaned or None


class UserUpdate(BaseModel):
    """Datos opcionales para actualizar un usuario."""

    email: EmailStr | None = Field(default=None, description="Correo del usuario.", example="usuario@gmail.com")
    name: str | None = Field(default=None, min_length=2, max_length=150, description="Nombre completo.", example="Alis Ureña")
    picture: str | None = Field(
        default=None,
        max_length=500,
        description="URL de foto de perfil.",
        example="https://lh3.googleusercontent.com/...",
    )

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("El nombre no puede estar vacío.")
        return cleaned

    @field_validator("picture")
    @classmethod
    def picture_strip_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        return cleaned or None


class UserResponse(BaseModel):
    """Información del usuario"""

    id: int = Field(..., description="ID único del usuario.", example=1)
    email: EmailStr = Field(..., description="Correo del usuario.", example="usuario@gmail.com")
    name: str = Field(..., description="Nombre completo.", example="Alis Ureña")
    picture: str | None = Field(
        default=None,
        description="URL de foto de perfil.",
        example="https://lh3.googleusercontent.com/...",
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "usuario@gmail.com",
                "name": "Alis Ureña",
                "picture": "https://lh3.googleusercontent.com/...",
            }
        },
    }


class UserListResponse(BaseModel):
    """Lista paginada de usuarios."""

    items: list[UserResponse] = Field(..., description="Lista de usuarios en la pagina actual.")
    total: int = Field(..., description="Total de usuarios que coinciden con el filtro.", example=42)
    page: int = Field(..., description="Pagina actual (empieza en 1).", example=1)
    page_size: int = Field(..., description="Cantidad de registros por pagina.", example=10)
    pages: int = Field(..., description="Total de paginas disponibles.", example=5)

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "email": "usuario@gmail.com",
                        "name": "Alis Ureña",
                        "picture": "https://lh3.googleusercontent.com/...",
                    }
                ],
                "total": 42,
                "page": 1,
                "page_size": 10,
                "pages": 5,
            }
        }
    }