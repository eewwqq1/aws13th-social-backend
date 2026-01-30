from typing import Optional, Annotated
from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, HttpUrl, model_validator



class UserSignUp(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=50)
    password_confirm: str
    nickname: Optional[str] = Field(default=None, min_length=2, max_length=20)
    profile_image_url: Optional[HttpUrl] = None

    @model_validator(mode="after")
    def password_match(self):
        if self.password != self.password_confirm:
            raise ValueError("패스워드 불일치")
        return self

class UserLogin(BaseModel):
    username: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(default=None, description="사용자 이메일")
    password: Optional[str] = Field(default=None, min_length=8, max_length=50)
    nickname: Optional[str] = Field(default=None, min_length=2, max_length=20)
    profile_image_url: Optional[HttpUrl] = None


def signup_form_reader(
    email: Annotated[EmailStr, Form(...)],
    password: Annotated[str, Form(...)],
    password_confirm: Annotated[str, Form(...)],
    nickname: Annotated[Optional[str], Form(...)] = None,
    profile_image_url: Annotated[Optional[HttpUrl], Form(...)] = None
) -> UserSignUp:
    return UserSignUp(
        email=email,
        password=password,
        password_confirm=password_confirm,
        nickname=nickname,
        profile_image_url=profile_image_url
    )

def login_form_reader(
    email: Annotated[EmailStr, Form(..., alias="username")],
    password: Annotated[str, Form(...)]
) -> UserLogin:
    return UserLogin(username=email, password=password)

def update_form_reader(
    email: Annotated[Optional[EmailStr], Form(...)] = None,
    password: Annotated[Optional[str], Form(...)] = None,
    nickname: Annotated[Optional[str], Form(...)] = None,
    profile_image_url: Annotated[Optional[HttpUrl], Form(...)] = None
) -> UserUpdate:
    return UserUpdate(
        email=email,
        password=password,
        nickname=nickname,
        profile_image_url=profile_image_url
    )
