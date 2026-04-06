from pydantic import BaseModel
from typing import Optional

class AuthRequest(BaseModel):
    phone: str
    otp_code: str  # In MVP, accept any 6-digit code

class AuthResponse(BaseModel):
    access_token: str
    user_id: str
    is_new_user: bool

class UserProfile(BaseModel):
    id: str
    display_name: str
    bio: str
    avatar_url: Optional[str] = None
    clout_score: float
    tier: str
    is_anchor: bool
    is_elite: bool

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
