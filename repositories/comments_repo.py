from fastapi import HTTPException


def get_all_comments(db):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM comments")
            return cursor.fetchall()

    except HTTPException:
        raise
    except Exception as e:
       print(f"Service Error: {e}")
       raise HTTPException(status_code=500, detail="Internal Server Error")


def get_comment_by_comment_id(db, comment_id):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM comments WHERE comment_id = %s", (comment_id,))
            return cursor.fetchone()

    except HTTPException:
        raise
    except Exception as e:
       print(f"Service Error: {e}")
       raise HTTPException(status_code=500, detail="Internal Server Error")
