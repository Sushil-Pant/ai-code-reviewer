"""Code review router."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db, User
from models.schemas import CodeReviewRequest, CodeReviewResponse, ReviewListItem
from services.review_service import (
    perform_code_review, get_review_by_id,
    get_user_reviews, delete_review
)
from utils.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_code(
    request: CodeReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit AI review."""
    try:
        review = await perform_code_review(db, current_user, request)

        # Build API response.
        issues_data = [
            {
                "id": issue.id,
                "severity": issue.severity,
                "category": issue.category,
                "description": issue.description,
                "fix": issue.fix,
                "line_number": issue.line_number
            }
            for issue in review.issues
        ]

        return {
            "id": review.id,
            "language": review.language,
            "overall_score": review.overall_score,
            "security_score": review.security_score,
            "performance_score": review.performance_score,
            "maintainability_score": review.maintainability_score,
            "total_issues": review.total_issues,
            "high_severity_count": review.high_severity_count,
            "medium_severity_count": review.medium_severity_count,
            "low_severity_count": review.low_severity_count,
            "issues": issues_data,
            "improved_code": review.improved_code,
            "created_at": review.created_at.isoformat(),
            "message": "Code review completed successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Review failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Code review failed. Please try again."
        )


@router.get("/history")
async def get_review_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    language: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get review history."""
    reviews = get_user_reviews(db, current_user.id, skip, limit, language)

    return {
        "reviews": [
            {
                "id": r.id,
                "language": r.language,
                "overall_score": r.overall_score,
                "security_score": r.security_score,
                "performance_score": r.performance_score,
                "maintainability_score": r.maintainability_score,
                "total_issues": r.total_issues,
                "high_severity_count": r.high_severity_count,
                "medium_severity_count": r.medium_severity_count,
                "low_severity_count": r.low_severity_count,
                "created_at": r.created_at.isoformat()
            }
            for r in reviews
        ],
        "total": len(reviews),
        "skip": skip,
        "limit": limit
    }


@router.get("/{review_id}")
async def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get review details."""
    review = get_review_by_id(db, review_id, current_user.id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    issues_data = [
        {
            "id": issue.id,
            "severity": issue.severity,
            "category": issue.category,
            "description": issue.description,
            "fix": issue.fix,
            "line_number": issue.line_number
        }
        for issue in review.issues
    ]

    return {
        "id": review.id,
        "language": review.language,
        "original_code": review.original_code,
        "improved_code": review.improved_code,
        "overall_score": review.overall_score,
        "security_score": review.security_score,
        "performance_score": review.performance_score,
        "maintainability_score": review.maintainability_score,
        "total_issues": review.total_issues,
        "high_severity_count": review.high_severity_count,
        "medium_severity_count": review.medium_severity_count,
        "low_severity_count": review.low_severity_count,
        "issues": issues_data,
        "created_at": review.created_at.isoformat()
    }


@router.delete("/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review_endpoint(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete code review."""
    success = delete_review(db, review_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    return {"message": "Review deleted successfully"}
