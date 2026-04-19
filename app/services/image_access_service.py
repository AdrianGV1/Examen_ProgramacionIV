from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from flask import current_app


class ImageAccessService:
    @staticmethod
    def generate_user_access_token(
        user_id: int,
        record_id: int,
        public_id: str,
        expires_minutes: int,
    ) -> dict:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=expires_minutes)

        payload = {
            "sub": str(user_id),
            "record_id": record_id,
            "public_id": public_id,
            "iat": now,
            "exp": expires_at,
            "type": "image_access",
            "jti": str(uuid4()),
        }

        token = jwt.encode(
            payload,
            current_app.config["JWT_SECRET_KEY"],
            algorithm=current_app.config.get("JWT_ALGORITHM", "HS256"),
        )

        return {
            "token": token,
            "expires_at": expires_at,
            "expires_in_seconds": int(expires_minutes * 60),
        }
