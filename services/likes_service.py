from datetime import datetime, timezone
from typing import Optional, List
import uuid
from models.like import LikeCreate, LikeResponse
from repositories.likes_repo import get_all_likes
from fastapi import HTTPException

def toggle_like_service(db, user_id: str, like_in: LikeCreate):

    target_column = "post_id" if like_in.target_type == "PostLike" else "comment_id"
    target_id = like_in.target_id

    try:
        with db.cursor() as cursor:
            check_sql = f"SELECT like_id FROM likes WHERE user_id = %s AND {target_column} = %s"
            cursor.execute(check_sql, (user_id, target_id))
            existing_like = cursor.fetchone()

            if existing_like:
                # 좋아요 취소
                like_id = existing_like['like_id']
                delete_sql = f"DELETE FROM likes WHERE like_id = %s"
                cursor.execute(delete_sql, (like_id,))
                is_liked = False
            else:
                # 좋아요 생성
                like_id = str(uuid.uuid4())
                insert_sql = f"""
                                    INSERT INTO likes (like_id, user_id, {target_column})
                                    VALUES (%s, %s, %s)
                                """
                # 여기서 target_id가 존재하지 않으면 DB가 Foreign Key 에러를 던짐
                cursor.execute(insert_sql, (like_id, user_id, target_id))
                is_liked = True
            db.commit()
            # 3. 최신 좋아요 총합 계산 (DB에 맡기기)
            count_sql = f"SELECT COUNT(*) as total FROM likes WHERE {target_column} = %s"
            cursor.execute(count_sql, (target_id,))
            total_likes = cursor.fetchone()['total']

        return LikeResponse(
            target_type=like_in.target_type,
            target_id=target_id,
            like_id=like_id,
            user_id=user_id,
            is_liked=is_liked,
            total_likes=total_likes
        )

    except Exception as e:
        db.rollback()
        # 에러 메시지에 'foreign key'가 포함되어 있다면 게시물/댓글이 없는 것
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(status_code=404, detail="해당 게시물이나 댓글을 찾을 수 없습니다.")
        # 그 외 DB 에러
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")


def get_likes_service(db, user_id: str, like_in: LikeCreate ) -> Optional[LikeResponse]:
    likes = get_all_likes(db)
    existing = next((like for like in likes if like["user_id"] == user_id
                     and like["target_type"] == like_in.target_type
                     and like["target_id"] == like_in.target_id), None)
    current_total = len([like for like in likes if
                         like["target_id"] == like_in.target_id and like["target_type"] == like_in.target_type])
    if not existing:

        return LikeResponse(
            target_type=like_in.target_type,
            target_id=like_in.target_id,
            like_id="",
            user_id=user_id,
            is_liked=False,
            total_likes=current_total
        )

    return LikeResponse(
        **existing,
        is_liked=True,
        total_likes=current_total
    )


def get_my_likes(user_id: str) -> List[dict]:
    likes = get_all_likes
    my_likes  = [like for like in likes if like["user_id"] == user_id]
    return my_likes

