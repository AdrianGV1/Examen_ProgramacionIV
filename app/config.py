
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.getenv("SECRET_KEY", "cambiar esto después")

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "radiografias")
UPLOAD_MAX_FILE_SIZE_MB = int(os.getenv("UPLOAD_MAX_FILE_SIZE_MB", "5"))
UPLOAD_MAX_FILE_SIZE_BYTES = UPLOAD_MAX_FILE_SIZE_MB * 1024 * 1024

_default_ext = "jpg,jpeg,png,webp"
UPLOAD_ALLOWED_EXTENSIONS = {
	ext.strip().lower()
	for ext in os.getenv("UPLOAD_ALLOWED_EXTENSIONS", _default_ext).split(",")
	if ext.strip()
}