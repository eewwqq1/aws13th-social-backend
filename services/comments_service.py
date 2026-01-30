from datetime import datetime, timezone
from typing import Optional
import uuid
from fastapi import HTTPException
from sqlalchemy import result_tuple

from models.comment import Comment, CommentResponse
from repositories.comments_repo import get_all_comments, get_comment_by_comment_id
from repositories.posts_repo import get_post_by_post_id

ALLOWED_COMMENT_FIELDS = frozenset({'content'})

def write_comments(db, post_id:str, data: Comment, current_user : dict):
    try:
        with db.cursor() as cursor:
            posts = get_post_by_post_id(db, post_id)
            if not posts :
                raise HTTPException(400, "Post ID not valid")
            comment_created_at = datetime.now(timezone.utc)
            user_id = current_user["user_id"]
            comment_id = str(uuid.uuid4())
            content = data.content

            insert_sql = "INSERT INTO comments (comment_id, post_id, user_id,content, created_at) VALUES (%s, %s, %s, %s, %s)"
            param = (comment_id, post_id, user_id, content, comment_created_at)
            cursor.execute(insert_sql, param)
            my_comment = CommentResponse(
                user_id = user_id,
                post_id = post_id,
                content=  content,
                comment_id= comment_id,
                created_at = comment_created_at
            ).model_dump(mode="json")
        db.commit()
        return my_comment

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        print(f"Service Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

def get_usr_comments(db, post_id:str, get_optional_user: Optional[dict] = None):
    all_data = get_all_comments(db)
    post_comments = [c for c in all_data if c["post_id"] == post_id]

    if not post_comments:
        raise HTTPException(status_code=404, detail="해당 게시물의 댓글을 찾을 수 없습니다.")

    if get_optional_user:
        user_id = get_optional_user.get("user_id")
        mine_only = [c for c in post_comments if c.get("user_id") == user_id]
        return mine_only

    return post_comments

def update_user_comments(db,comment_id:str, data: Comment, current_user : dict):
    try:
        with db.cursor() as cursor:
            user_comment = get_comment_by_comment_id(db, comment_id)
            if user_comment is None:
                raise HTTPException(status_code=404, detail="해당 댓글을 찾을수 없습니다")
            if user_comment["user_id"] != current_user["user_id"]:
                raise HTTPException(status_code=403, detail=" 댓글을 수정할 권한이 없습니다.")

            data_dict = data.model_dump(mode="json")
            safe_fields = [k for k in data_dict.keys() if k in ALLOWED_COMMENT_FIELDS]
            if not safe_fields:
                raise HTTPException(status_code=401, detail="유효한 필드가 아닙니다.")
            sql_fields = ",".join([f"`{key}` = %s" for key in safe_fields])
            update_sql = "UPDATE comments SET " + sql_fields + " WHERE comment_id = %s"
            values = [data_dict[k] for k in safe_fields]
            values.append(comment_id)
            cursor.execute(update_sql, tuple(values))

            select_sql = "SELECT * FROM comments WHERE comment_id = %s"
            cursor.execute(select_sql, (comment_id,))
            updated_comment_row = cursor.fetchone()
            if not updated_comment_row:
                raise HTTPException(status_code=404, detail="해당 댓글을 찾을수 없습니다.")

        db.commit()
        return updated_comment_row

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        print(f"Service Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



def delete_user_comments(db, comment_id:str, current_user : dict ):
    comments = get_comment_by_comment_id(db, comment_id)
    if not comments:
        raise HTTPException(status_code=404, detail="코멘트를 찾을 수 없습니다.")

    if comments["user_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="본인의 댓글만 삭제할 수 있습니다."
        )
    updated_posts = [p for p in comments if p["comment_id"] != comment_id]

def get_my_comment(db, current_user : dict):
    all_data = get_all_comments(db)
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="인증이 필요합니다")
    return [c for c in all_data if c.get("user_id") == user_id]