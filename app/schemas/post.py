from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    video_key: str
    prompt_text: str
    duration_seconds: int = 0

class PostResponse(BaseModel):
    id: str
    author_id: str
    author_name: str
    author_tier: str
    video_url: str
    prompt_text: str
    view_count: int
    reply_count: int
    like_count: int
    is_boosted: bool
    created_at: datetime

class ReplyCreate(BaseModel):
    video_key: str
    duration_seconds: int = 0

class ReplyResponse(BaseModel):
    id: str
    post_id: str
    author_id: str
    author_name: str
    video_url: str
    rank_score: float
    is_boosted: bool
    like_count: int
    is_seen: bool
    is_liked_by_poster: bool
    created_at: datetime
