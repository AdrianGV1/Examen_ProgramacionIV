
from flask_openapi3 import Info, Tag

API_INFO = Info(
    title="Gestión de Placas Radiográficas",
    version="1.0.0",
    description=(
        "API para la gestión de placas radiográficas de pacientes. "
        "Permite registrar pacientes, subir imágenes radiográficas a Cloudinary "
        "y consultar/actualizar los registros existentes.\n\n"
        "**Autenticación:** Todos los endpoints (excepto `/auth/login`) "
        "requieren un JWT en el header `Authorization: Bearer <token>`.\n\n"
        "El token se obtiene completando el flujo de Google SSO en `/auth/login`."
    ),
)


TAG_AUTH = Tag(name="Auth", description="Autenticación con Google SSO y manejo de JWT.")
TAG_RADIOGRAPHS = Tag(name="Radiographs", description="CRUD de placas radiográficas de pacientes.")
TAG_USERS = Tag(name="Users", description="Información del usuario autenticado.")
TAG_UPLOADS = Tag(name="Uploads", description="Subida y eliminación de imágenes en Cloudinary.")
TAG_UPLOADS = Tag(name="Uploads", description="Subida y eliminación de imágenes en Cloudinary.")

SECURITY_SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT obtenido tras autenticarse con Google SSO.",
    }
}