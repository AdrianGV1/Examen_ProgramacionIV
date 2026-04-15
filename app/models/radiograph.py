from datetime import datetime

from app.extensions import db


class Radiograph(db.Model):
	__tablename__ = "radiographs"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	patient_name = db.Column(db.String(255), nullable=False)
	patient_id_number = db.Column(db.String(100), nullable=False)
	clinical_reference = db.Column(db.String(255), nullable=False)
	study_date = db.Column(db.Date, nullable=False)
	image_url = db.Column(db.String(500), nullable=True)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	updated_at = db.Column(
		db.DateTime,
		nullable=False,
		default=datetime.utcnow,
		onupdate=datetime.utcnow,
	)

	def __repr__(self) -> str:
		return (
			f"<Radiograph id={self.id} patient_id_number='{self.patient_id_number}' "
			f"study_date={self.study_date}>"
		)
