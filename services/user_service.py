from fastapi import HTTPException
from models.user import UserPublic
from repositories.user_repo import get_user_by_user_id
from services.auth_service import get_password_hash
from datetime import datetime, timezone

# 백틱 금지. 동적으로 컬럼 생성하는거니까 절대 백틱금지! 써야하는 경우
ALLOWED_USER_FIELDS = frozenset({'email', 'password', 'nickname', 'profile_image_url'})
TABLES = ["posts","comments", "likes"]

def get_my_profile(current_user: dict) -> dict:
    return current_user

def get_user_profile(db,user_id: str) -> dict:
    users = get_user_by_user_id(db, user_id)
    if not users:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다")
    return users

def update_my_profile(db, current_user: dict, patch_data: dict) -> dict:
    if not patch_data:
        raise HTTPException(status_code=400, detail="수정할 데이터가 없습니다.")

    if "email" in patch_data:
        new_email = patch_data["email"]
        if new_email != current_user["email"]:
           with db.cursor() as cursor:
               cursor.execute("SELECT user_id FROM users WHERE email = %s", (new_email,))
               if cursor.fetchone():
                   raise HTTPException(status_code=409, detail="이미 사용중인 이메일 입니다.")

    if "password" in patch_data :
        patch_data["password"] = get_password_hash(patch_data["password"])

    try:
        with db.cursor() as cursor:
            safe_fields= [k for k in patch_data.keys() if k in ALLOWED_USER_FIELDS]
            if not safe_fields:
                raise HTTPException(status_code=400, detail="유효한 필드가 아닙니다.")

            sql_fields = ",".join([f"`{key}` = %s"for key in safe_fields])
            update_sql = "UPDATE users SET " + sql_fields + " WHERE user_id = %s"

            values = [patch_data[k] for k in safe_fields]
            values.append(current_user["user_id"])

            cursor.execute(update_sql, tuple(values))

            select_sql = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(select_sql, (current_user["user_id"],))
            updated_user_row = cursor.fetchone()
            if not updated_user_row:
                raise HTTPException(status_code=404, detail="해당 유저를 찾을 수 없습니다.")
        db.commit()
        update_user = UserPublic(**updated_user_row).model_dump(mode="json")
        print(update_user)
        print(current_user)
        return update_user

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        print(f"Service Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def delete_my_account(db,current_user: dict) -> None:
    try:
        with db.cursor() as cursor:
            delete_time = datetime.now(timezone.utc)
            update_sql = "UPDATE users SET is_activate = 0, deleted_at = %s WHERE user_id = %s"
            cursor.execute(update_sql, (delete_time, current_user["user_id"]))

            user_deleted = cursor.rowcount

            # posts, comments, likes 테이블 is_actives 일괄 처리
            # dbms가 아닌 서비스 코드에서 처리 함
            for table in TABLES:
                sql= "UPDATE " + table +" SET is_activate = 0, deleted_at = %s WHERE user_id = %s AND is_activate = 1"
                cursor.execute(sql, (delete_time, current_user["user_id"]))

            if user_deleted == 0:
                raise HTTPException(status_code=404, detail="해당 유저가 없습니다")

        db.commit()

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        print(f"Service Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

