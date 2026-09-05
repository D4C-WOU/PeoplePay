from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin


class SalaryStructure(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "salary_structures"

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    rules: Mapped[list["SalaryRule"]] = relationship(
        back_populates="salary_structure",
    )

    contracts: Mapped[list["Contract"]] = relationship(
        back_populates="salary_structure",
    )