from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class DailyPromptOut(BaseModel):
    id: str
    text: str
    category: str
    active_date: date
    total_responses: int

    class Config:
        from_attributes = True


class PromptCreateIn(BaseModel):
    text: str
    category: str
    active_date: date
