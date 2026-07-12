"""Database configuration setup."""

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from utils.config import settings

# Setup database engine.
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database table models.

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    reviews = relationship("CodeReview", back_populates="user")


class CodeReview(Base):
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    language = Column(String(20), nullable=False)
    original_code = Column(Text, nullable=False)
    improved_code = Column(Text, nullable=True)

    # Model review scores.
    overall_score = Column(Float, default=0.0)
    security_score = Column(Float, default=0.0)
    performance_score = Column(Float, default=0.0)
    maintainability_score = Column(Float, default=0.0)

    # Model review metadata.
    total_issues = Column(Integer, default=0)
    high_severity_count = Column(Integer, default=0)
    medium_severity_count = Column(Integer, default=0)
    low_severity_count = Column(Integer, default=0)

    # Model raw response.
    raw_response = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    issues = relationship("ReviewIssue", back_populates="review", cascade="all, delete-orphan")


class ReviewIssue(Base):
    __tablename__ = "review_issues"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("code_reviews.id"), nullable=False)
    severity = Column(String(20), nullable=False)   # Issue severity levels.
    category = Column(String(50), nullable=False)   # Issue category tags.
    description = Column(Text, nullable=False)
    fix = Column(Text, nullable=True)
    line_number = Column(Integer, nullable=True)

    review = relationship("CodeReview", back_populates="issues")


# Database utility helpers.

def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Yield database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
