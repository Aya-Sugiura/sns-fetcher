from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List

from api.models import SNSPost, SNSPostCreate, HealthCheck

app = FastAPI(
    title="SNS Fetcher API",
    description="SNSデータ取得・管理API",
    version="0.1.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のオリジンのみを許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# インメモリデータストア（開発用）
posts_db: List[SNSPost] = []
next_id = 1


@app.get("/", tags=["Root"])
async def root():
    """ルートエンドポイント"""
    return {
        "message": "SNS Fetcher API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """ヘルスチェックエンドポイント"""
    return HealthCheck(
        status="ok",
        timestamp=datetime.now()
    )


@app.get("/posts", response_model=List[SNSPost], tags=["Posts"])
async def get_posts(platform: str = None):
    """
    投稿一覧を取得

    - **platform**: プラットフォームでフィルタリング（オプション）
    """
    if platform:
        return [post for post in posts_db if post.platform == platform]
    return posts_db


@app.get("/posts/{post_id}", response_model=SNSPost, tags=["Posts"])
async def get_post(post_id: int):
    """
    特定の投稿を取得

    - **post_id**: 投稿ID
    """
    for post in posts_db:
        if post.id == post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")


@app.post("/posts", response_model=SNSPost, status_code=201, tags=["Posts"])
async def create_post(post: SNSPostCreate):
    """
    新しい投稿を作成

    - **post**: 投稿データ
    """
    global next_id

    new_post = SNSPost(
        id=next_id,
        platform=post.platform,
        content=post.content,
        author=post.author,
        url=post.url,
        created_at=datetime.now()
    )

    posts_db.append(new_post)
    next_id += 1

    return new_post


@app.put("/posts/{post_id}", response_model=SNSPost, tags=["Posts"])
async def update_post(post_id: int, post: SNSPostCreate):
    """
    投稿を更新

    - **post_id**: 投稿ID
    - **post**: 更新データ
    """
    for i, existing_post in enumerate(posts_db):
        if existing_post.id == post_id:
            updated_post = SNSPost(
                id=post_id,
                platform=post.platform,
                content=post.content,
                author=post.author,
                url=post.url,
                created_at=existing_post.created_at
            )
            posts_db[i] = updated_post
            return updated_post

    raise HTTPException(status_code=404, detail="Post not found")


@app.delete("/posts/{post_id}", tags=["Posts"])
async def delete_post(post_id: int):
    """
    投稿を削除

    - **post_id**: 投稿ID
    """
    for i, post in enumerate(posts_db):
        if post.id == post_id:
            deleted_post = posts_db.pop(i)
            return {"message": "Post deleted", "post": deleted_post}

    raise HTTPException(status_code=404, detail="Post not found")
