"""add departments and employee relationship

Revision ID: 2684f69eb294
Revises: f02f3a139218
Create Date: 2026-08-14 23:41:35.907984

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "2684f69eb294"
down_revision: Union[str, Sequence[str], None] = "f02f3a139218"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # 1. Create departments table
    op.create_table(
        "departments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "code",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    # 2. Add department_id temporarily as nullable
    op.add_column(
        "employees",
        sa.Column(
            "department_id",
            sa.Uuid(),
            nullable=True,
        ),
    )

    # 3. Create a default department
    department_id = "00000000-0000-0000-0000-000000000001"

    op.execute(
        sa.text(
            """
            INSERT INTO departments (
                id,
                name,
                code,
                description,
                is_active
            )
            VALUES (
                :id,
                :name,
                :code,
                :description,
                :is_active
            )
            """
        ).bindparams(
            id=department_id,
            name="General",
            code="GEN",
            description="Default department",
            is_active=True,
        )
    )

    # 4. Assign existing employees to General department
    op.execute(
        sa.text(
            """
            UPDATE employees
            SET department_id = :department_id
            WHERE department_id IS NULL
            """
        ).bindparams(
            department_id=department_id,
        )
    )

    # 5. Now make department_id NOT NULL
    op.alter_column(
        "employees",
        "department_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )

    # 6. Add foreign key
    op.create_foreign_key(
        "fk_employees_department_id",
        "employees",
        "departments",
        ["department_id"],
        ["id"],
    )

    # 7. Remove old department column
    op.drop_column(
        "employees",
        "department",
    )


def downgrade() -> None:

    # 1. Restore old department column
    op.add_column(
        "employees",
        sa.Column(
            "department",
            sa.String(length=100),
            nullable=True,
        ),
    )

    # 2. Remove foreign key
    op.drop_constraint(
        "fk_employees_department_id",
        "employees",
        type_="foreignkey",
    )

    # 3. Remove department_id
    op.drop_column(
        "employees",
        "department_id",
    )

    # 4. Remove departments table
    op.drop_table(
        "departments",
    )