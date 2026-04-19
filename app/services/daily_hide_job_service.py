import os
import atexit
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app import config
from app.extensions import db
from app.repositories.radiograph_repository import RadiographRepository
from app.services.upload_service import UploadService, UploadServiceError


scheduler = BackgroundScheduler()
logger = logging.getLogger(__name__)
_scheduler_lock_fd = None
_scheduler_lock_path = None


def _is_pid_running(pid: int) -> bool:
	if pid <= 0:
		return False

	try:
		os.kill(pid, 0)
		return True
	except ProcessLookupError:
		return False
	except PermissionError:
		# El proceso existe pero no tenemos permisos para señalizarlo.
		return True
	except OSError:
		return False


def _release_scheduler_lock() -> None:
	global _scheduler_lock_fd
	global _scheduler_lock_path

	if _scheduler_lock_fd is not None:
		try:
			os.close(_scheduler_lock_fd)
		except OSError:
			pass
		finally:
			_scheduler_lock_fd = None

	if _scheduler_lock_path:
		try:
			os.remove(_scheduler_lock_path)
		except OSError:
			pass
		finally:
			_scheduler_lock_path = None


def _acquire_scheduler_lock() -> bool:
	global _scheduler_lock_fd
	global _scheduler_lock_path

	lock_path = os.path.abspath(config.DAILY_HIDE_SCHEDULER_LOCK_FILE)
	_scheduler_lock_path = lock_path

	for _ in range(2):
		try:
			fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
			os.write(fd, str(os.getpid()).encode("utf-8"))
			_scheduler_lock_fd = fd
			return True
		except FileExistsError:
			try:
				with open(lock_path, "r", encoding="utf-8") as lock_file:
					content = lock_file.read().strip()
				stale_pid = int(content) if content.isdigit() else -1
			except OSError:
				stale_pid = -1

			if stale_pid > 0 and _is_pid_running(stale_pid):
				return False

			# lock stale: intentamos eliminarlo y reintentar una vez
			try:
				os.remove(lock_path)
			except OSError:
				return False

	return False


def run_daily_hide_job() -> None:
	hidden_at = datetime.utcnow()
	records = RadiographRepository.list_public_images_for_daily_hide(db.session)
	total = len(records)
	success = 0
	failures = 0

	logger.info("daily_hide_job started: %s candidate records", total)

	for record in records:
		try:
			UploadService.make_image_private(record.image_public_id)
			RadiographRepository.mark_image_hidden(record, hidden_at)
			success += 1
		except UploadServiceError:
			failures += 1
			logger.exception(
				"daily_hide_job failed for record_id=%s public_id=%s",
				record.id,
				record.image_public_id,
			)
			continue

	db.session.commit()
	logger.info(
		"daily_hide_job finished: total=%s success=%s failures=%s",
		total,
		success,
		failures,
	)


def init_daily_hide_scheduler(app) -> None:
	if scheduler.running:
		return

	if not config.ENABLE_DAILY_HIDE_SCHEDULER:
		logger.info("daily_hide_scheduler disabled by config")
		return

	# Evita duplicar el scheduler con el reloader de Flask en desarrollo.
	if app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
		return

	if not _acquire_scheduler_lock():
		logger.info("daily_hide_scheduler not started: lock already acquired by another process")
		return

	atexit.register(_release_scheduler_lock)

	trigger = CronTrigger(
		hour=config.IMAGE_HIDE_HOUR,
		minute=config.IMAGE_HIDE_MINUTE,
		timezone=ZoneInfo(config.IMAGE_HIDE_TIMEZONE),
	)

	def _job_wrapper() -> None:
		with app.app_context():
			run_daily_hide_job()

	scheduler.add_job(
		_job_wrapper,
		trigger=trigger,
		id="daily_hide_images",
		replace_existing=True,
	)
	scheduler.start()
	logger.info("daily_hide_scheduler started in pid=%s", os.getpid())