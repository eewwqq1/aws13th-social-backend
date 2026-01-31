from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from core.db_connection import get_db
from dependencies.auth import get_current_user
from models.auth import UserSignUp, UserLogin, UserUpdate, signup_form_reader, update_form_reader
from models.user import AuthResponse, UserPublic
from services.auth_service import signup_user, login_user
from services.user_service import get_my_profile, get_user_profile, update_my_profile, delete_my_account

router = APIRouter(tags=["users"])

@router.post("/auth/signup",response_model=AuthResponse,status_code=status.HTTP_201_CREATED)
async def signup(
        form_data: Annotated[UserSignUp, Depends(signup_form_reader)],
        db = Depends(get_db)
):
    user_internal, token, expires = signup_user(db, form_data)
    return AuthResponse(
        access_token=token,
        expires_in=expires,
        user=UserPublic(**user_internal.model_dump(include={"email", "nickname", "profile_image_url"})),
        issued_at=datetime.now(timezone.utc),
    )

@router.post("/auth/login",response_model=AuthResponse)
async def login(
        form_data : Annotated[OAuth2PasswordRequestForm,Depends()],
        db = Depends(get_db)
):
    data = UserLogin(
        username=form_data.username,
        password=form_data.password,
    )
    user, token, expires = login_user(db, data)
    return AuthResponse(
        access_token=token,
        expires_in=expires,
        user=user,
        issued_at=datetime.now(timezone.utc),
    )

@router.get("/users/me",response_model=UserPublic)
async def get_user_me(current_user: Annotated[dict, Depends(get_current_user)]):
    return get_my_profile(current_user)

@router.get("/users/{user_id}", response_model=UserPublic)
async def get_user(user_id: str, db = Depends(get_db)):
    return get_user_profile(db,user_id)

@router.patch("/users/me",response_model=UserUpdate)
async def update_user(
        update_data : Annotated[UserUpdate, Depends(update_form_reader)],
        current_user:  Annotated[dict, Depends(get_current_user)],
        db = Depends(get_db)
):
    patch_dict = update_data.model_dump(exclude_unset=True, exclude_none=True,mode="json")
    return update_my_profile(db,current_user, patch_dict)


@router.delete("/users/me",status_code=status.HTTP_200_OK)
async def delete_user(
        current_user: Annotated[dict, Depends(get_current_user)],
        db = Depends(get_db)
):
    delete_my_account(db,current_user)
    return {"user_id": "삭제되었음"}
