from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from os.path import splitext
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import cloudinary
import cloudinary.uploader
import cloudinary.utils
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app import config
from app.schemas.errors import ErrorCodes
from app.schemas.upload import UploadResponse


@dataclass
class UploadServiceError(Exception):
	code: str
	message: str
	status_code: int


class UploadService:
	_ALLOWED_MIME_TYPES = {
		"image/jpeg",
		"image/png",
		"image/webp",
	}

	_configured = False

	@classmethod
	def _configure_cloudinary(cls) -> None:
		if cls._configured:
			return

		if not config.CLOUDINARY_CLOUD_NAME or not config.CLOUDINARY_API_KEY or not config.CLOUDINARY_API_SECRET:
			raise UploadServiceError(
				code=ErrorCodes.INTERNAL_ERROR,
				message="Cloudinary no esta configurado en variables de entorno",
				status_code=500,
			)

		cloudinary.config(
			cloud_name=config.CLOUDINARY_CLOUD_NAME,
			api_key=config.CLOUDINARY_API_KEY,
			api_secret=config.CLOUDINARY_API_SECRET,
			secure=True,
		)
		cls._configured = True

	@staticmethod
	def _validate_extension(filename: str) -> None:
		cleaned_name = secure_filename(filename or "")
		if "." not in cleaned_name:
			raise UploadServiceError(
				code=ErrorCodes.INVALID_FILE_TYPE,
				message="El archivo debe tener extension valida",
				status_code=400,
			)

		extension = cleaned_name.rsplit(".", 1)[1].lower()
		if extension not in config.UPLOAD_ALLOWED_EXTENSIONS:
			raise UploadServiceError(
				code=ErrorCodes.INVALID_FILE_TYPE,
				message=f"Tipo de archivo no permitido: .{extension}",
				status_code=400,
			)

	@classmethod
	def _validate_mime_type(cls, file: FileStorage) -> None:
		mime_type = (file.mimetype or "").lower()
		if mime_type not in cls._ALLOWED_MIME_TYPES:
			raise UploadServiceError(
				code=ErrorCodes.INVALID_FILE_TYPE,
				message=f"MIME type no permitido: {mime_type or 'desconocido'}",
				status_code=400,
			)

	@staticmethod
	def _validate_file_size(file: FileStorage) -> None:
		file.stream.seek(0, 2)
		file_size = file.stream.tell()
		file.stream.seek(0)

		if file_size <= 0:
			raise UploadServiceError(
				code=ErrorCodes.VALIDATION_ERROR,
				message="El archivo esta vacio",
				status_code=400,
			)

		if file_size > config.UPLOAD_MAX_FILE_SIZE_BYTES:
			raise UploadServiceError(
				code=ErrorCodes.FILE_TOO_LARGE,
				message=(
					f"Archivo excede el tamano maximo de "
					f"{config.UPLOAD_MAX_FILE_SIZE_MB} MB"
				),
				status_code=400,
			)

	@classmethod
	def upload_image(cls, file: FileStorage) -> UploadResponse:
		if file is None:
			raise UploadServiceError(
				code=ErrorCodes.VALIDATION_ERROR,
				message="No se recibio archivo",
				status_code=400,
			)

		cls._configure_cloudinary()
		cls._validate_extension(file.filename or "")
		cls._validate_mime_type(file)
		cls._validate_file_size(file)

		try:
			result = cloudinary.uploader.upload(
				file,
				folder=config.UPLOAD_FOLDER,
				resource_type="image",
			)
		except Exception as exc:
			raise UploadServiceError(
				code=ErrorCodes.INTERNAL_ERROR,
				message="Error al subir archivo a Cloudinary",
				status_code=502,
			) from exc

		url = result.get("secure_url") or result.get("url")
		public_id = result.get("public_id")
		if not url or not public_id:
			raise UploadServiceError(
				code=ErrorCodes.INTERNAL_ERROR,
				message="Cloudinary no retorno URL o public_id",
				status_code=502,
			)

		return UploadResponse(url=url, public_id=public_id)

	@classmethod
	def delete_image(cls, public_id: str) -> bool:
		if not public_id or not public_id.strip():
			raise UploadServiceError(
				code=ErrorCodes.VALIDATION_ERROR,
				message="public_id es requerido",
				status_code=400,
			)

		cls._configure_cloudinary()

		try:
			result = cloudinary.uploader.destroy(public_id.strip(), resource_type="image")
		except Exception as exc:
			raise UploadServiceError(
				code=ErrorCodes.INTERNAL_ERROR,
				message="Error al eliminar imagen en Cloudinary",
				status_code=502,
			) from exc

		return result.get("result") == "ok"

	@classmethod
	def make_image_private(cls, public_id: str) -> None:
		if not public_id or not public_id.strip():
			raise UploadServiceError(
				code=ErrorCodes.VALIDATION_ERROR,
				message="public_id es requerido",
				status_code=400,
			)

		cls._configure_cloudinary()

		try:
			cloudinary.uploader.explicit(
				public_id.strip(),
				resource_type="image",
				type="upload",
				access_mode="authenticated",
			)
		except Exception as exc:
			raise UploadServiceError(
				code=ErrorCodes.INTERNAL_ERROR,
				message="No se pudo marcar la imagen como privada en Cloudinary",
				status_code=502,
			) from exc

	@staticmethod
	def _infer_format_from_image_url(image_url: str | None) -> str:
		if not image_url:
			return "png"

		try:
			parsed = urlparse(image_url)
			ext = splitext(parsed.path)[1].lower().lstrip(".")
			if ext:
				return ext
		except Exception:
			pass

		return "png"

	@staticmethod
	def _append_query_param(url: str, key: str, value: str) -> str:
		parsed = urlparse(url)
		query_items = parse_qsl(parsed.query, keep_blank_values=True)
		query_items.append((key, value))
		new_query = urlencode(query_items)
		return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

	@classmethod
	def generate_temporary_signed_url(
		cls,
		public_id: str,
		expires_minutes: int,
		user_access_token: str,
		image_url: str | None = None,
	) -> dict:
		if not public_id or not public_id.strip():
			raise UploadServiceError(
				code=ErrorCodes.VALIDATION_ERROR,
				message="public_id es requerido",
				status_code=400,
			)

		if expires_minutes < 1 or expires_minutes > 60:
			raise UploadServiceError(
				code=ErrorCodes.VALIDATION_ERROR,
				message="expires_minutes debe estar entre 1 y 60",
				status_code=400,
			)

		if not user_access_token or not user_access_token.strip():
			raise UploadServiceError(
				code=ErrorCodes.VALIDATION_ERROR,
				message="user_access_token es requerido",
				status_code=400,
			)

		cls._configure_cloudinary()

		expires_at_dt = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
		expires_at_unix = int(expires_at_dt.timestamp())
		file_format = cls._infer_format_from_image_url(image_url)

		try:
			signed_url = cloudinary.utils.private_download_url(
				public_id.strip(),
				file_format,
				resource_type="image",
				type="upload",
				expires_at=expires_at_unix,
			)
		except Exception as exc:
			raise UploadServiceError(
				code=ErrorCodes.INTERNAL_ERROR,
				message="No se pudo generar URL firmada temporal",
				status_code=502,
			) from exc

		signed_url = cls._append_query_param(signed_url, "user_token", user_access_token)

		return {
			"signed_url": signed_url,
			"expires_at": expires_at_dt,
			"expires_in_seconds": int(expires_minutes * 60),
		}
