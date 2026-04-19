
from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str = Field(
        ...,
        description="Token JWT para autenticar las siguientes peticiones.",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo de token. Siempre bearer.",
        example="bearer",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    }


class UserInfoResponse(BaseModel):
    id: int = Field(..., description="ID unico del usuario.", example=1)
    email: EmailStr = Field(..., description="Correo electronico.", example="usuario@gmail.com")
    name: str = Field(..., description="Nombre completo.", example="Alis Ureña")
    picture: str | None = Field(
        default=None,
        description="URL de foto de perfil de Google.",
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