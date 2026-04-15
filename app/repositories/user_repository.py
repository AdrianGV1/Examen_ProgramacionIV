from sqlalchemy import func

from app.models.user import User


class UserRepository:
	@staticmethod
	def create(db, data: dict) -> User:
		record = User(**data)
		db.add(record)
		db.commit()
		db.refresh(record)
		return record

	@staticmethod
	def get_by_id(db, record_id: int) -> User | None:
		return db.get(User, record_id)

	@staticmethod
	def get_all(db, page, page_size, name, email, order_by, order_dir) -> tuple[list, int]:
		page = max(int(page or 1), 1)
		page_size = max(int(page_size or 10), 1)

		query = db.query(User)

		if name:
			query = query.filter(User.name.ilike(f"%{name.strip()}%"))

		if email:
			query = query.filter(User.email == email.strip())

		total = query.with_entities(func.count(User.id)).scalar() or 0

		sort_column = getattr(User, order_by, None) if order_by else User.created_at
		if sort_column is None:
			sort_column = User.created_at

		sort_direction = (order_dir or "desc").lower()
		if sort_direction == "asc":
			query = query.order_by(sort_column.asc())
		else:
			query = query.order_by(sort_column.desc())

		records = query.offset((page - 1) * page_size).limit(page_size).all()
		return records, total

	@staticmethod
	def update(db, record_id: int, data: dict) -> User | None:
		record = db.get(User, record_id)
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
		record = db.get(User, record_id)
		if record is None:
			return False

		db.delete(record)
		db.commit()
		return True
