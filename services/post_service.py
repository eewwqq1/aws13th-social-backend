from datetime import datetime, timezone
from typing import Optional
import uuid
from fastapi import HTTPException
from models.post import Post, PostQuery, PostPublic
from repositories.posts_repo import get_post_by_post_id, get_all_posts

ALLOWED_POST_FIELDS = frozenset({'title', 'content'})

def write_posts(db, data: Post, current_user: dict):
    try:
        with db.cursor() as cursor:

            #posts 테이블 title에 unique조건 활성화 - race condition 해소
            user_id = current_user["user_id"]
            post_id = str(uuid.uuid4())
            post_created_at = datetime.now(timezone.utc)

            insert_sql = "INSERT INTO posts (user_id, post_id,title, content, media, created_at) VALUES (%s, %s, %s, %s, %s, %s)"
            param =(user_id, post_id, data.title, data.content, data.media, post_created_at)
            cursor.execute(insert_sql, param)

            post_response= PostPublic(
                title=data.title,
                content=data.content,
                media=data.media,
            )
        db.commit()
        return post_response

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        print(f"Service Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

def get_user_post(db, post_id: str) -> dict:
    try:
        with db.cursor() as cursor:
            user_post = get_post_by_post_id(db, post_id)

            if not user_post:
                raise HTTPException(status_code=404, detail="해당 게시물을 찾을수 없습니다.")

            if "view_count" not in user_post:
                user_post["view_count"] = 0

            cursor.execute("UPDATE posts SET view_count = view_count + 1 WHERE post_id = %s", (post_id,))
            db.commit()
            return user_post

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        print(f"Service Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

def update_my_post(db, post_id:str, post_dict: dict, current_user: dict) -> dict:
    try:
        with db.cursor() as cursor:
            user_post = get_post_by_post_id(db, post_id)
            if user_post is None:
                raise HTTPException(status_code=404, detail="해당 게시물을 찾을수 없습니다")
            if user_post["user_id"] != current_user["user_id"]:
                raise HTTPException(status_code=403, detail="게시물을 수정할 권한이 없습니다.")

            safe_fields = [k for k in post_dict.keys() if k in ALLOWED_POST_FIELDS]
            if not safe_fields:
                raise HTTPException(status_code=401, detail="유효한 필드가 아닙니다.")
            sql_fields = ",".join([f"`{key}` = %s" for key in safe_fields])
            update_sql = "UPDATE posts SET " + sql_fields + " WHERE post_id = %s"
            values = [post_dict[k] for k in safe_fields]
            values.append(post_id)
            cursor.execute(update_sql, tuple(values))

            select_sql = "SELECT * FROM posts WHERE post_id = %s"
            cursor.execute(select_sql, (post_id,))
            updated_post_row = cursor.fetchone()
            if not updated_post_row:
                raise HTTPException(status_code=404, detail="해당 게시물을 찾을수 없습니다.")

        db.commit()
        return PostPublic(**updated_post_row).model_dump(mode="json")

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        print(f"Service Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

def delete_my_post(db, post_id:str, current_user: dict) -> None:
    try:
        with db.cursor() as cursor:
            user_post = get_post_by_post_id(db, post_id)
            if not user_post:
                 raise HTTPException(status_code=404, detail="게시물을 찾을 수 없습니다.")
            if user_post["user_id"] != current_user["user_id"]:
                raise HTTPException(status_code=403, detail="본인의 게시물만 삭제할 수 있습니다." )
            delete_time = datetime.now(timezone.utc)
            update_sql = "UPDATE posts SET is_activate=0, deleted_at = %s WHERE post_id = %s"
            cursor.execute(update_sql, (delete_time, post_id,))

            deleted_row = cursor.rowcount
            if deleted_row == 0:
             raise HTTPException(status_code=404, detail="삭제가 이루어지지 않았습니다")

        db.commit()

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        print(f"Service Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")




def query_post(db, param: PostQuery, get_optional_user: Optional[dict]) -> dict:
    data = get_all_posts(db)

    if get_optional_user :
        return data
    else:
        pass

    if param.search:
        search_item = param.search.lower()
        data = [post for post in data if search_item in post.get("title","").lower()]

    if not data:
        raise HTTPException(
            status_code=404,
            detail= f"검색어 {param.search}에 해당하는 게시물을 찾을수 없습니다."
        )

    reverse = True if param.sort_order == "desc" else False
    data = sorted(data, key=lambda x: x[param.sort_by], reverse=reverse)
    paged_data = data[param.start_idx: param.end_idx]

    return {
        "total": len(data),
        "page": param.page,
        "size": param.size,
        "results": paged_data
    }
