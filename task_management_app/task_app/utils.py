import uuid
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta


class BCruptUtil:

    SALT = bcrypt.gensalt()
    UTF_8 = "utf-8"

    @staticmethod
    def encrypt_password(plain_password: str) -> str:
        return bcrypt.hashpw(
            plain_password.encode(BCruptUtil.UTF_8), BCruptUtil.SALT
        ).decode(BCruptUtil.UTF_8)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode(BCruptUtil.UTF_8),
            hashed_password.encode(BCruptUtil.UTF_8),
        )


class JWTUtil:

    SECRET_KEY = "airtribe-jwt-api-token-for-backend"
    ALGORITHM = "HS256"
    EXPIRY_MINUTES = 15

    @staticmethod
    def create_token(user_id: uuid | str) -> str:
        user_id = str(user_id)
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=JWTUtil.EXPIRY_MINUTES),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, JWTUtil.SECRET_KEY, algorithm=JWTUtil.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            payload = jwt.decode(
                token, JWTUtil.SECRET_KEY, algorithms=[JWTUtil.ALGORITHM]
            )
            return {"valid": True, "user_id": payload["user_id"]}
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token has expired."}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token."}
