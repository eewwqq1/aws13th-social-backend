from fastapi import HTTPException


def get_all_comments(db):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM comments WHERE is_activate=1")
            return cursor.fetchall()

    except HTTPException:
        raise
    except Exception as e:
       print(f"Service Error: {e}")
       raise HTTPException(status_code=500, detail="Internal Server Error")


def get_comment_by_post_id(db, post_id):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM comments WHERE post_id=%s AND is_activate=1", (post_id,))
            return cursor.fetchall()
    except HTTPException:
        raise
    except Exception as e:
        print(f"Service Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



def get_comment_by_comment_id(db, comment_id):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM comments WHERE comment_id = %s AND is_activate=1", (comment_id,))
            return cursor.fetchone()

    except HTTPException:
        raise
    except Exception as e:
       print(f"Service Error: {e}")
       raise HTTPException(status_code=500, detail="Internal Server Error")
