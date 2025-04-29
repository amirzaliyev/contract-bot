from sqlalchemy import BIGINT, ForeignKey, BINARY, CheckConstraint, text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import ENUM
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Status(PyEnum):
    PRIVATE = "private"
    PUBLIC = "public"

class Document(Base):

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str]
    owner_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(
        ENUM(
            Status,
            values_callable=lambda x: [i.value for i in x]
        ),
        server_default=Status.PRIVATE.value
    )
    file_path: Mapped[str]
    tg_file_id: Mapped[str | None]
    is_template: Mapped[bool] = mapped_column(default=False, server_default=text("FALSE"))

    owner: Mapped['User'] = relationship(back_populates="documents")

    # # Add a check constraint
    # __table_args__ = (
    #     CheckConstraint(
    #         "(is_template = TRUE OR status = 'private')",
    #         name="check_status_private_if_not_template"
    #     )
    # )