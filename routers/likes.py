from typing import Annotated
from pymysql import IntegrityError
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from core.db_connection import get_db
from dependencies.auth import get_current_user
from models.like import LikeResponse, LikeCreate
from repositories.comments_repo import get_all_comments, get_comment_by_comment_id
from repositories.posts_repo import get_all_posts, get_post_by_post_id
from services.likes_service import toggle_like_service, get_likes_service, get_my_likes

router = APIRouter(tags=["likes"])

# @router.post("/likes", response_model=LikeResponse)
# def toggle_like(
#     like_in: LikeCreate,
#     current_user: Annotated[dict, Depends(get_current_user)],
#     db = Depends(get_db)
# ):
#     return toggle_like_service(db, current_user["user_id"], like_in)


@router.post("/posts/{post_id}/likes", response_model=LikeResponse)
def post_like_post(
            post_id: str,
            current_user: Annotated[dict, Depends(get_current_user)],
            db = Depends(get_db)
    ):
    user_id = current_user["user_id"]
    like_in = LikeCreate(target_type="PostLike", target_id=post_id)
    try:
        return toggle_like_service(db, user_id,like_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=404, detail="해당 게시물을 찾을 수 없습니다.")


@router.post("/comments/{comment_id}/likes", response_model=LikeResponse)
def post_like_comment(
    comment_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    db = Depends(get_db)
):
    user_id = current_user["user_id"]
    like_in = LikeCreate(target_type="CommentLike", target_id=comment_id)
    try:
        return toggle_like_service(db, user_id,like_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=404, detail="해당 게시물을 찾을 수 없습니다.")

@router.get("/posts/{post_id}/likes", response_model=LikeResponse)
def get_likes_post(
        post_id: str,
        current_user: Annotated[dict, Depends(get_current_user)],
        db = Depends(get_db)
):
    user_id = current_user["user_id"]
    like_in = LikeCreate(target_type="PostLike", target_id=post_id)
    try:
        return toggle_like_service(db, user_id,like_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=404, detail="해당 게시물을 찾을 수 없습니다.")

@router.get("/comments/{comment_id}/likes", response_model=LikeResponse)
def get_like_comment(
        comment_id: str,
        current_user: Annotated[dict, Depends(get_current_user)],
        db = Depends(get_db)
):
    user_id = current_user["user_id"]
    like_in = LikeCreate(target_type="CommentLike", target_id=comment_id)
    try:
        return toggle_like_service(db, user_id,like_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=404, detail="해당 게시물을 찾을 수 없습니다.")

@router.get("/likes/me")
def like_me(current_user: Annotated[dict, Depends(get_current_user)]):
    user_id = current_user["user_id"]
    return get_my_likes(user_id)

