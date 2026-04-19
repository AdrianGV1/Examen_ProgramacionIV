from math import ceil

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate


class UserService:
	@staticmethod
	def create_record(db, payload: UserCreate) -> UserResponse:
		required_fields = ("email", "name")
		missing_fields = [
			field
			for field in required_fields
			if getattr(payload, field, None) is None
			or (isinstance(getattr(payload, field), str) and not getattr(payload, field).strip())
		]
		if missing_fields:
			raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

		try:
			record = UserRepository.create(db, payload.model_dump())
		except IntegrityError as exc:
			db.rollback()
			raise ValueError("El email ya existe") from exc

		return UserResponse.model_validate(record)

	@staticmethod
	def get_record(db, record_id: int) -> UserResponse:
		record = UserRepository.get_by_id(db, record_id)
		if record is None:
			raise NotFound(description="User record not found")
		return UserResponse.model_validate(record)

	@staticmethod
	def list_records(db, page, page_size, name, email, order_by, order_dir) -> UserListResponse:
		normalized_page = max(int(page or 1), 1)
		normalized_page_size = max(int(page_size or 10), 1)

		records, total = UserRepository.get_all(
			db=db,
			page=normalized_page,
			page_size=normalized_page_size,
			name=name,
			email=email,
			order_by=order_by,
			order_dir=order_dir,
		)

		items = [UserResponse.model_validate(record) for record in records]
		pages = ceil(total / normalized_page_size) if total > 0 else 0

		return UserListResponse(
			items=items,
			total=total,
			page=normalized_page,
			page_size=normalized_page_size,
			pages=pages,
		)

	@staticmethod
	def update_record(db, record_id: int, payload: UserUpdate) -> UserResponse:
		update_data = payload.model_dump(exclude_unset=True)
		try:
			record = UserRepository.update(db, record_id, update_data)
		except IntegrityError as exc:
			db.rollback()
			raise ValueError("El email ya existe") from exc
		if record is None:
			raise NotFound(description="User record not found")
		return UserResponse.model_validate(record)

	@staticmethod
	def delete_record(db, record_id: int) -> bool:
		deleted = UserRepository.delete(db, record_id)
		if not deleted:
			raise NotFound(description="User record not found")
		return True
