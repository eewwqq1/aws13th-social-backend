from fastapi import HTTPException

def get_all_likes(db):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM likes")
            return cursor.fetchall()
    except HTTPException:
        raise
    except Exception as e:
       print(f"Service Error: {e}")
       raise HTTPException(status_code=500, detail="Internal Server Error")



def get_like_by_like_id(db, like_id):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM likes WHERE like_id = %s", (like_id,))
            return cursor.fetchone()
    except HTTPException:
        raise
    except Exception as e:
       print(f"Service Error: {e}")
       raise HTTPException(status_code=500, detail="Internal Server Error")


