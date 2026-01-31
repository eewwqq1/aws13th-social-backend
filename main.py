from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import posts, users, comments, likes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vue 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(comments.router)
app.include_router(likes.router)

@app.get("/")
async def read_root():
    return {"root": "루트입니다"}
