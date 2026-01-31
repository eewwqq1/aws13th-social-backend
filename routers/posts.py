from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from core.db_connection import get_db
from dependencies.auth import get_current_user, get_optional_user
from models.post import PostPublic, Post, post_form_reader, PostQuery
from services.post_service import write_posts, get_user_post, update_my_post, delete_my_post, query_post

router = APIRouter(tags=["posts"])

@router.post("/posts", response_model=PostPublic)
async def create_post(
        post_data:Annotated[Post, Depends(post_form_reader)],
        current_user : Annotated[dict,Depends(get_current_user)],
        db = Depends(get_db),
):
    return write_posts(db,post_data, current_user)

@router.get("/posts")
async def get_posts(
        current_user: Annotated[Optional[dict], Depends(get_optional_user)],
        post_query_param: Annotated[PostQuery, Depends()] = None,
        db = Depends(get_db),
):
    return query_post(db, post_query_param, current_user)

@router.get("/posts/{post_id}",response_model=PostPublic)
async def get_post(post_id: str,
                   db= Depends(get_db)):
    return get_user_post(db, post_id)

@router.patch("/posts/{post_id}")
async def update_post(
        post_id:str,
        post_data: Annotated[Post, Depends(post_form_reader)],
        current_user: Annotated[dict, Depends(get_current_user)],
        db = Depends(get_db)
):
    post_dict = post_data.model_dump(exclude_unset=True, mode="json")
    return update_my_post(db,post_id,post_dict, current_user)

@router.delete("/posts/{post_id}")
async def delete_post(
        post_id:str,
        current_user: Annotated[dict, Depends(get_current_user)],
        db = Depends(get_db)
):
    delete_my_post(db, post_id, current_user)
    return {"post_id": "삭제 되었습니다."}


