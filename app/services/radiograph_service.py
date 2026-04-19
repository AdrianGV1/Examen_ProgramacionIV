from datetime import datetime
from math import ceil

from werkzeug.exceptions import NotFound

from app.repositories.radiograph_repository import RadiographRepository
from app.services.upload_service import UploadService
from app.schemas.radiograph import (
	RadiographCreate,
	RadiographListResponse,
	RadiographResponse,
	RadiographUpdate,
)


class RadiographService:
	@staticmethod
	def _normalize_image_visibility(data: dict) -> dict:
		if "image_hidden_at" in data and data.get("image_hidden_at") is not None and "image_is_private" not in data:
			data["image_is_private"] = True

		if "image_is_private" in data:
			if data.get("image_is_private") is True and data.get("image_hidden_at") is None:
				data["image_hidden_at"] = datetime.utcnow()
			elif data.get("image_is_private") is False:
				data["image_hidden_at"] = None

		return data

	@staticmethod
	def create_record(db, payload: RadiographCreate) -> RadiographResponse:
		required_fields = (
			"patient_name",
			"patient_id_number",
			"clinical_reference",
			"study_date",
		)

		missing_fields = [
			field
			for field in required_fields
			if getattr(payload, field, None) is None
			or (isinstance(getattr(payload, field), str) and not getattr(payload, field).strip())
		]
		if missing_fields:
			raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

		create_data = payload.model_dump(exclude_unset=True)
		create_data = RadiographService._normalize_image_visibility(create_data)

		# Si se crea como privada, asegurar que Cloudinary quede en modo authenticated.
		if create_data.get("image_is_private") is True:
			public_id = create_data.get("image_public_id")
			if not public_id:
				raise ValueError("image_public_id es requerido para marcar la imagen como privada")
			UploadService.make_image_private(public_id)

		record = RadiographRepository.create(db, create_data)
		return RadiographResponse.model_validate(record)

	@staticmethod
	def get_record(db, record_id: int) -> RadiographResponse:
		record = RadiographRepository.get_by_id(db, record_id)
		if record is None:
			raise NotFound(description="Radiograph record not found")

		return RadiographResponse.model_validate(record)

	@staticmethod
	def list_records(
		db,
		page,
		page_size,
		patient_name,
		patient_id_number,
		study_date_from,
		study_date_to,
		order_by,
		order_dir,
	) -> RadiographListResponse:
		normalized_page = max(int(page or 1), 1)
		normalized_page_size = max(int(page_size or 10), 1)

		records, total = RadiographRepository.get_all(
			db=db,
			page=normalized_page,
			page_size=normalized_page_size,
			patient_name=patient_name,
			patient_id_number=patient_id_number,
			study_date_from=study_date_from,
			study_date_to=study_date_to,
			order_by=order_by,
			order_dir=order_dir,
		)

		items = [RadiographResponse.model_validate(record) for record in records]
		pages = ceil(total / normalized_page_size) if total > 0 else 0

		return RadiographListResponse(
			items=items,
			total=total,
			page=normalized_page,
			page_size=normalized_page_size,
			pages=pages,
		)

	@staticmethod
	def update_record(db, record_id: int, payload: RadiographUpdate) -> RadiographResponse:
		update_data = payload.model_dump(exclude_unset=True)
		update_data = RadiographService._normalize_image_visibility(update_data)

		record = RadiographRepository.get_by_id(db, record_id)
		if record is None:
			raise NotFound(description="Radiograph record not found")

		# Si se marca como privada, asegurar que Cloudinary quede en modo authenticated.
		if update_data.get("image_is_private") is True:
			public_id = update_data.get("image_public_id") or record.image_public_id
			if not public_id:
				raise ValueError("image_public_id es requerido para marcar la imagen como privada")
			UploadService.make_image_private(public_id)

		record = RadiographRepository.update(db, record_id, update_data)
		return RadiographResponse.model_validate(record)

	@staticmethod
	def delete_record(db, record_id: int) -> bool:
		deleted = RadiographRepository.delete(db, record_id)
		if not deleted:
			raise NotFound(description="Radiograph record not found")

		return True
