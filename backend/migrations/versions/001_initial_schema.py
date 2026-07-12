"""Initial schema — users, code_reviews, review_issues

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users ──────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── code_reviews ───────────────────────────────────────────
    op.create_table(
        "code_reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(20), nullable=False),
        sa.Column("original_code", sa.Text(), nullable=False),
        sa.Column("improved_code", sa.Text(), nullable=True),
        sa.Column("overall_score", sa.Float(), nullable=True, default=0.0),
        sa.Column("security_score", sa.Float(), nullable=True, default=0.0),
        sa.Column("performance_score", sa.Float(), nullable=True, default=0.0),
        sa.Column("maintainability_score", sa.Float(), nullable=True, default=0.0),
        sa.Column("total_issues", sa.Integer(), nullable=True, default=0),
        sa.Column("high_severity_count", sa.Integer(), nullable=True, default=0),
        sa.Column("medium_severity_count", sa.Integer(), nullable=True, default=0),
        sa.Column("low_severity_count", sa.Integer(), nullable=True, default=0),
        sa.Column("raw_response", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_code_reviews_id", "code_reviews", ["id"])

    # ── review_issues ──────────────────────────────────────────
    op.create_table(
        "review_issues",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("review_id", sa.Integer(), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("fix", sa.Text(), nullable=True),
        sa.Column("line_number", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["review_id"], ["code_reviews.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_review_issues_id", "review_issues", ["id"])


def downgrade() -> None:
    op.drop_table("review_issues")
    op.drop_table("code_reviews")
    op.drop_table("users")
