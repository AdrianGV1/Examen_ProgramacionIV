
from pydantic import BaseModel, EmailStr, Field


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