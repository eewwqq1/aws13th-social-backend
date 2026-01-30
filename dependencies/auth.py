from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from starlette.requests import Request
from core.config import jwt_settings
from core.db_connection import get_db
from repositories.user_repo import get_user_by_user_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = jwt.decode(
            token,
            jwt_settings.SECRET_KEY,
            algorithms=[jwt_settings.ALGORITHM],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰 페이로드")

        user = get_user_by_user_id(db, user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다")
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="토큰 인증에 실패했습니다.")
    except Exception as e:
        print(f"Auth Error: {e}")  # 로깅
        raise HTTPException(status_code=500, detail="인증 처리 중 서버 오류가 발생했습니다.")


def get_optional_user(request: Request) -> Optional[dict]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1]
    try:
        payload = jwt.decode(
            token,
            jwt_settings.SECRET_KEY,
            algorithms=[jwt_settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None
