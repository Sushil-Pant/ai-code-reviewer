"""Code review service."""

import json
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from database.db import CodeReview, ReviewIssue, User
from models.schemas import CodeReviewRequest, CodeReviewResponse, ReviewListItem
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


async def perform_code_review(
    db: Session,
    user: User,
    request: CodeReviewRequest
) -> CodeReview:
    """Perform code review."""
    logger.info(f"Starting review for user {user.id}, language: {request.language}")

    # Run AI analysis.
    analysis = await gemini_service.analyze_code(request.code, request.language.value)

    # Count severity levels.
    issues = analysis.get("issues", [])
    high_count = sum(1 for i in issues if i.get("severity") == "High")
    medium_count = sum(1 for i in issues if i.get("severity") == "Medium")
    low_count = sum(1 for i in issues if i.get("severity") == "Low")

    # Create review record.
    review = CodeReview(
        user_id=user.id,
        language=request.language.value,
        original_code=request.code,
        improved_code=analysis.get("improved_code", ""),
        overall_score=float(analysis.get("overall_score", 0)),
        security_score=float(analysis.get("security_score", 0)),
        performance_score=float(analysis.get("performance_score", 0)),
        maintainability_score=float(analysis.get("maintainability_score", 0)),
        total_issues=len(issues),
        high_severity_count=high_count,
        medium_severity_count=medium_count,
        low_severity_count=low_count,
        raw_response=json.dumps(analysis)
    )
    db.add(review)
    db.flush()  # Flush database changes.

    # Save review issues.
    for issue_data in issues:
        issue = ReviewIssue(
            review_id=review.id,
            severity=issue_data.get("severity", "Medium"),
            category=issue_data.get("category", "Code Smell"),
            description=issue_data.get("description", ""),
            fix=issue_data.get("fix", ""),
            line_number=issue_data.get("line_number")
        )
        db.add(issue)

    db.commit()
    db.refresh(review)

    logger.info(f"Review {review.id} created: score={review.overall_score}, issues={len(issues)}")
    return review


def get_review_by_id(db: Session, review_id: int, user_id: int) -> Optional[CodeReview]:
    """Get user review."""
    return db.query(CodeReview).filter(
        CodeReview.id == review_id,
        CodeReview.user_id == user_id
    ).first()


def get_user_reviews(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    language: Optional[str] = None
) -> List[CodeReview]:
    """Get user reviews."""
    query = db.query(CodeReview).filter(CodeReview.user_id == user_id)

    if language:
        query = query.filter(CodeReview.language == language)

    return query.order_by(CodeReview.created_at.desc()).offset(skip).limit(limit).all()


def delete_review(db: Session, review_id: int, user_id: int) -> bool:
    """Delete user review."""
    review = get_review_by_id(db, review_id, user_id)
    if not review:
        return False
    db.delete(review)
    db.commit()
    return True


def get_dashboard_stats(db: Session, user_id: int) -> dict:
    """Get dashboard statistics."""
    from sqlalchemy import func

    reviews = db.query(CodeReview).filter(CodeReview.user_id == user_id)
    total = reviews.count()

    if total == 0:
        return {
            "total_reviews": 0,
            "average_score": 0.0,
            "average_security_score": 0.0,
            "average_performance_score": 0.0,
            "average_maintainability_score": 0.0,
            "total_issues_found": 0,
            "high_severity_total": 0,
            "languages_used": {},
            "recent_reviews": []
        }

    # Calculate aggregate statistics.
    agg = db.query(
        func.avg(CodeReview.overall_score).label("avg_overall"),
        func.avg(CodeReview.security_score).label("avg_security"),
        func.avg(CodeReview.performance_score).label("avg_performance"),
        func.avg(CodeReview.maintainability_score).label("avg_maintainability"),
        func.sum(CodeReview.total_issues).label("total_issues"),
        func.sum(CodeReview.high_severity_count).label("total_high"),
    ).filter(CodeReview.user_id == user_id).first()

    # Group by language.
    lang_rows = db.query(
        CodeReview.language,
        func.count(CodeReview.id).label("cnt")
    ).filter(CodeReview.user_id == user_id).group_by(CodeReview.language).all()

    languages_used = {row.language: row.cnt for row in lang_rows}

    # Fetch recent reviews.
    recent = reviews.order_by(CodeReview.created_at.desc()).limit(10).all()
    recent_data = [
        {
            "id": r.id,
            "language": r.language,
            "overall_score": r.overall_score,
            "total_issues": r.total_issues,
            "high_severity_count": r.high_severity_count,
            "created_at": r.created_at
        }
        for r in recent
    ]

    return {
        "total_reviews": total,
        "average_score": round(float(agg.avg_overall or 0), 1),
        "average_security_score": round(float(agg.avg_security or 0), 1),
        "average_performance_score": round(float(agg.avg_performance or 0), 1),
        "average_maintainability_score": round(float(agg.avg_maintainability or 0), 1),
        "total_issues_found": int(agg.total_issues or 0),
        "high_severity_total": int(agg.total_high or 0),
        "languages_used": languages_used,
        "recent_reviews": recent_data
    }
