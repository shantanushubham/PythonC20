import logging
import uuid
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class BCruptUtil:

    SALT = bcrypt.gensalt()
    UTF_8 = "utf-8"

    @staticmethod
    def encrypt_password(plain_password: str) -> str:
        logger.info("op=encrypt_password")
        return bcrypt.hashpw(
            plain_password.encode(BCruptUtil.UTF_8), BCruptUtil.SALT
        ).decode(BCruptUtil.UTF_8)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        result = bcrypt.checkpw(
            plain_password.encode(BCruptUtil.UTF_8),
            hashed_password.encode(BCruptUtil.UTF_8),
        )
        logger.info("op=verify_password status=%s", "success" if result else "failed")
        return result


class JWTUtil:

    SECRET_KEY = "airtribe-jwt-api-token-for-backend"
    ALGORITHM = "HS256"
    EXPIRY_MINUTES = 15

    @staticmethod
    def create_token(user_id: uuid | str) -> str:
        user_id = str(user_id)
        logger.info("op=create_token user_id=%s", user_id)
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=JWTUtil.EXPIRY_MINUTES),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, JWTUtil.SECRET_KEY, algorithm=JWTUtil.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> dict:
        logger.info("op=verify_token")
        try:
            payload = jwt.decode(
                token, JWTUtil.SECRET_KEY, algorithms=[JWTUtil.ALGORITHM]
            )
            logger.info("op=verify_token status=success user_id=%s", payload["user_id"])
            return {"valid": True, "user_id": payload["user_id"]}
        except jwt.ExpiredSignatureError:
            logger.warning("op=verify_token status=failed reason=token_expired")
            return {"valid": False, "error": "Token has expired."}
        except jwt.InvalidTokenError:
            logger.warning("op=verify_token status=failed reason=invalid_token")
            return {"valid": False, "error": "Invalid token."}
