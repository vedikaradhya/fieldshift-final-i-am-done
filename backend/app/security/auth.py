from datetime import datetime, timedelta, timezone
from hashlib import sha256
from uuid import uuid4
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db.session import get_db
from app.models import RevokedToken, SessionToken, User

hasher = PasswordHasher()
bearer = HTTPBearer()

def hash_password(password: str) -> str: return hasher.hash(password)
def verify_password(password: str, hashed: str) -> bool:
    try: return hasher.verify(hashed, password)
    except VerifyMismatchError: return False

def token_id_hash(token_id: str) -> str: return sha256(token_id.encode()).hexdigest()

def _create_token(user: User, token_type: str, expires_delta: timedelta) -> tuple[str, str, datetime]:
    token_id, expires_at = uuid4().hex, datetime.now(timezone.utc) + expires_delta
    payload = {"sub": str(user.id), "role": user.role.value, "jti": token_id, "typ": token_type, "iat": datetime.now(timezone.utc), "exp": expires_at}
    return jwt.encode(payload, get_settings().secret_key, algorithm="HS256"), token_id, expires_at

def create_access_token(user: User) -> str:
    token, _, _ = _create_token(user, "access", timedelta(minutes=get_settings().access_token_expire_minutes))
    return token

def create_refresh_token(user: User, db: Session) -> str:
    token, token_id, expires_at = _create_token(user, "refresh", timedelta(days=get_settings().refresh_token_expire_days))
    db.add(SessionToken(user_id=user.id, token_id_hash=token_id_hash(token_id), expires_at=expires_at))
    return token

def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from error
    if payload.get("typ") != expected_type or not payload.get("jti"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    return payload

def revoke_token_id(db: Session, token_id: str, expires_at: datetime) -> None:
    hashed = token_id_hash(token_id)
    if not db.scalar(select(RevokedToken).where(RevokedToken.token_id_hash == hashed)):
        db.add(RevokedToken(token_id_hash=hashed, expires_at=expires_at))

def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    payload = decode_token(credentials.credentials, "access")
    if db.scalar(select(RevokedToken).where(RevokedToken.token_id_hash == token_id_hash(payload["jti"]))):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive account")
    return user
