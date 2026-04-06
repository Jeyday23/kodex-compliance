from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationOut(BaseModel):
    id: str
    type: str
    title: str
    body: str
    related_user_id: Optional[str] = None
    related_post_id: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
