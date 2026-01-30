from fastapi import HTTPException

def get_all_posts(db):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE is_activate=1")
            return cursor.fetchall()
    except HTTPException:
        raise
    except Exception as e:
       print(f"Service Error: {e}")
       raise HTTPException(status_code=500, detail="Internal Server Error")

def get_post_by_post_id(db, post_id):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE post_id = %s AND is_activate=1 ", (post_id,))
            return cursor.fetchone()
    except HTTPException:
        raise
    except Exception as e:
       print(f"Service Error: {e}")
       raise HTTPException(status_code=500, detail="Internal Server Error")

