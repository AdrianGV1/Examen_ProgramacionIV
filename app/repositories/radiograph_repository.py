from sqlalchemy import func

from app.models.radiograph import Radiograph


class RadiographRepository:
	@staticmethod
	def create(db, data: dict) -> Radiograph:
		record = Radiograph(**data)
		db.add(record)
		db.commit()
		db.refresh(record)
		return record

	@staticmethod
	def get_by_id(db, record_id: int) -> Radiograph | None:
		return db.get(Radiograph, record_id)

	@staticmethod
	def get_all(
		db,
		page,
		page_size,
		patient_name,
		patient_id_number,
		study_date_from,
		study_date_to,
		order_by,
		order_dir,
	) -> tuple[list, int]:
		page = max(int(page or 1), 1)
		page_size = max(int(page_size or 10), 1)

		query = db.query(Radiograph)

		if patient_name:
			query = query.filter(Radiograph.patient_name.ilike(f"%{patient_name.strip()}%"))

		if patient_id_number:
			query = query.filter(Radiograph.patient_id_number == patient_id_number)

		if study_date_from:
			query = query.filter(Radiograph.study_date >= study_date_from)

		if study_date_to:
			query = query.filter(Radiograph.study_date <= study_date_to)

		total = query.with_entities(func.count(Radiograph.id)).scalar() or 0

		sort_column = getattr(Radiograph, order_by, None) if order_by else Radiograph.created_at
		if sort_column is None:
			sort_column = Radiograph.created_at

		sort_direction = (order_dir or "desc").lower()
		if sort_direction == "asc":
			query = query.order_by(sort_column.asc())
		else:
			query = query.order_by(sort_column.desc())

		records = query.offset((page - 1) * page_size).limit(page_size).all()
		return records, total

	@staticmethod
	def update(db, record_id: int, data: dict) -> Radiograph | None:
		record = db.get(Radiograph, record_id)
		if record is None:
			return None

		for field, value in data.items():
			if hasattr(record, field):
				setattr(record, field, value)

		db.commit()
		db.refresh(record)
		return record

	@staticmethod
	def delete(db, record_id: int) -> bool:
		record = db.get(Radiograph, record_id)
		if record is None:
			return False

		db.delete(record)
		db.commit()
		return True
