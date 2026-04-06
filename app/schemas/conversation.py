from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class MessageOut(BaseModel):
    id: str
    sender_id: str
    sender_name: str = ""
    body: str
    video_key: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MessageIn(BaseModel):
    body: str
    video_key: Optional[str] = None


class ConversationOut(BaseModel):
    id: str
    partner_id: str
    partner_name: str
    partner_avatar_key: Optional[str] = None
    last_message: Optional[str] = None
    unread_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
