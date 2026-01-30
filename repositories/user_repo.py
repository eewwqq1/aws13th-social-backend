
from fastapi import HTTPException

def get_user_by_user_id(db, user_id):
    try:
       with db.cursor() as cursor:
            cursor.execute("SELECT user_id, email, nickname, profile_image_url FROM users WHERE user_id = %s AND is_activate=1", (user_id,))
            return cursor.fetchone()

    except HTTPException:
        raise

    except Exception as e:
       print(f"Service Error: {e}")
       raise HTTPException(status_code=500, detail="Internal Server Error")



