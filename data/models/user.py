from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import text, BIGINT, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .contract import Contract

class UserRole(PyEnum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class Lang(PyEnum):
    UZ = "uz"
    EN = "en"
    RU = "ru"

class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    username: Mapped[str | None]
    phone_number: Mapped[str]
    reports_to: Mapped[int | None]
    language_code: Mapped[str] = mapped_column(
        ENUM(Lang, values_callable=lambda x: [i.value for i in x]),
        server_default=Lang.UZ.value
    )
    role: Mapped[str] = mapped_column(
        ENUM(UserRole, values_callable=lambda x: [i.value for i in x]), 
        server_default=UserRole.USER.value
    )

    is_admin: Mapped[bool] = mapped_column(default=False)
    is_suspicious: Mapped[bool] = mapped_column(default=False)
    is_block: Mapped[bool] = mapped_column(default=False)
    is_premium: Mapped[bool] = mapped_column(default=False)

    contracts: Mapped[list['Contract']] = relationship(back_populates="owner")

