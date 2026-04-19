
import os
from dotenv import load_dotenv

load_dotenv()

# ========================
# Base de Datos
# ========================
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# ========================
# Flask & Seguridad
# ========================
SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-esto-después")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# ========================
# Google OAuth (Flask-Dance)
# ========================
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# ========================
# JWT (PyJWT)
# ========================
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRES_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60"))

# ========================
# Cloudinary
# ========================
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

# ========================
# Upload de Archivos
# ========================
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "radiografias")
UPLOAD_MAX_FILE_SIZE_MB = int(os.getenv("UPLOAD_MAX_FILE_SIZE_MB", "5"))
UPLOAD_MAX_FILE_SIZE_BYTES = UPLOAD_MAX_FILE_SIZE_MB * 1024 * 1024

_default_ext = "jpg,jpeg,png,webp"
UPLOAD_ALLOWED_EXTENSIONS = {
	ext.strip().lower()
	for ext in os.getenv("UPLOAD_ALLOWED_EXTENSIONS", _default_ext).split(",")
	if ext.strip()
}

# ========================
# Job Diario de Ocultamiento
# ========================
IMAGE_HIDE_HOUR = int(os.getenv("IMAGE_HIDE_HOUR", "23"))
IMAGE_HIDE_MINUTE = int(os.getenv("IMAGE_HIDE_MINUTE", "59"))
IMAGE_HIDE_TIMEZONE = os.getenv("IMAGE_HIDE_TIMEZONE", "America/Costa_Rica")
ENABLE_DAILY_HIDE_SCHEDULER = os.getenv("ENABLE_DAILY_HIDE_SCHEDULER", "true").lower() == "true"
DAILY_HIDE_SCHEDULER_LOCK_FILE = os.getenv(
	"DAILY_HIDE_SCHEDULER_LOCK_FILE",
	".daily_hide_scheduler.lock",
)

# ========================
# Acceso temporal a imágenes ocultas
# ========================
SIGNED_IMAGE_URL_EXPIRES_MINUTES = int(os.getenv("SIGNED_IMAGE_URL_EXPIRES_MINUTES", "10"))