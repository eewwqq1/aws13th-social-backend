import os
from pathlib import Path
import pymysql
from dotenv import load_dotenv
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB
from starlette.exceptions import HTTPException

BASE_DIR = Path(__file__).resolve().parent
dotenv_db_path = BASE_DIR / ".env_DB"

# verbose=True를 넣으면 로드 과정을 상세히 출력해줍니다.
if load_dotenv(dotenv_path=dotenv_db_path, verbose=True):
    print(f"✅ .env_DB 로드 성공! (경로: {dotenv_db_path})")
else:
    print(f"❌ .env_DB 로드 실패! (파일이 해당 경로에 있는지 확인하세요: {dotenv_db_path})")
def get_env(key:str, default=None):
    value = os.getenv(key, default)
    if value is None:
        raise RuntimeError(f"환경변수 누락 : {key}")
    return value
db_config = {
    "host": get_env("MYSQL_HOST","localhost"),
    "port": int(get_env("MYSQL_PORT", 3306)),
    "db": get_env("MYSQL_DB", "my_app"),
    "user": get_env("MYSQL_USER","root"),
    "password": get_env("MYSQL_PASSWORD"),
    "charset": get_env("MYSQL_CHARSET","utf8mb4"),
    "cursorclass" : DictCursor
}

pools = PooledDB(
    creator=pymysql,
    mincached=5,
    maxcached=10,
    maxconnections=20,
    blocking=True, # 풀이 찼을 때 대기 여부
    **db_config
)

def get_db_connection():
    return pools.connection()

def get_db():
    conn = get_db_connection()
    try:
        yield conn
    except Exception as e:
        print(f"DB error: {e}")
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    finally:
        conn.close()
