"""Data validation schemas."""

from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


# Define custom enums.

class ProgrammingLanguage(str, Enum):
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    CPP = "cpp"
    C = "c"


class SeverityLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class IssueCategory(str, Enum):
    SECURITY = "Security"
    PERFORMANCE = "Performance"
    BUG = "Bug"
    CODE_SMELL = "Code Smell"
    MAINTAINABILITY = "Maintainability"
    CODING_STANDARDS = "Coding Standards"


# Define authentication schemas.

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    @validator("username")
    def username_alphanumeric(cls, v):
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must be alphanumeric")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

    @validator("password")
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# Define review schemas.

class CodeReviewRequest(BaseModel):
    code: str
    language: ProgrammingLanguage

    @validator("code")
    def code_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Code cannot be empty")
        if len(v) > 50000:
            raise ValueError("Code exceeds maximum length of 50,000 characters")
        return v


class IssueSchema(BaseModel):
    severity: SeverityLevel
    category: IssueCategory
    description: str
    fix: str
    line_number: Optional[int] = None

    class Config:
        from_attributes = True


class CodeReviewResponse(BaseModel):
    id: int
    language: str
    overall_score: float
    security_score: float
    performance_score: float
    maintainability_score: float
    total_issues: int
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int
    issues: List[IssueSchema]
    improved_code: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewListItem(BaseModel):
    id: int
    language: str
    overall_score: float
    total_issues: int
    high_severity_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# Define dashboard schemas.

class DashboardStats(BaseModel):
    total_reviews: int
    average_score: float
    average_security_score: float
    average_performance_score: float
    average_maintainability_score: float
    total_issues_found: int
    high_severity_total: int
    languages_used: dict
    recent_reviews: List[ReviewListItem]


# Define gemini schemas.

class GeminiIssue(BaseModel):
    severity: str
    category: str
    description: str
    fix: str
    line_number: Optional[int] = None


class GeminiAnalysisResult(BaseModel):
    overall_score: int
    security_score: int
    performance_score: int
    maintainability_score: int
    issues: List[GeminiIssue]
    improved_code: str
    summary: Optional[str] = ""
