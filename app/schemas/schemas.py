from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict

class UrlStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"

class UrlEnvironmentEnum(str, Enum):
    production = "production"
    staging = "staging"
    testing = "testing"
    other = "other"

# --- User Schemas ---
class UserBase(BaseModel):
    id: str
    email: str
    name: str
    role: str = "Administrator"

class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: str = "Administrator"

class UserLogin(BaseModel):
    # Support both username or email to match both tv_admin web app (username) and Flutter (email)
    username: Optional[str] = None
    email: Optional[str] = None
    password: str

class LoginResponse(BaseModel):
    success: bool = True
    user: UserBase
    token: str

# --- URL Schemas ---
class UrlItemBase(BaseModel):
    # Support both 'name' (Flutter) and 'title' (Web admin)
    title: Optional[str] = None
    name: Optional[str] = None
    
    # Support both 'url' (Web admin) and 'address' (Flutter)
    url: Optional[str] = None
    address: Optional[str] = None
    
    category: Optional[str] = "General"
    description: Optional[str] = ""
    notes: Optional[str] = ""
    environment: Optional[str] = "production"
    status: str = "active"
    refreshInterval: Optional[int] = 0

class UrlItemCreate(UrlItemBase):
    pass

class UrlItemUpdate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    environment: Optional[str] = None
    status: Optional[str] = None
    refreshInterval: Optional[int] = None

class UrlItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    name: str
    url: str
    address: str
    category: str
    description: str
    notes: str
    environment: str
    status: str
    refreshInterval: int
    createdAt: str
    updatedAt: str

