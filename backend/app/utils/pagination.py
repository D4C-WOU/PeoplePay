from math import ceil
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.schemas.pagination import Page


def paginate_scalars(
    db: Session,
    stmt: Select[Any],
    page: int,
    page_size: int,
) -> Page[Any]:
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    pages = ceil(total / page_size) if total else 0
    items = list(
        db.scalars(stmt.offset((page - 1) * page_size).limit(page_size))
        .unique()
        .all()
    )
    return Page(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
