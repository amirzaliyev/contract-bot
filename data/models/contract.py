from sqlalchemy import BIGINT, ForeignKey, BINARY
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import ENUM
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .contract_details import ContractDetails


class Status(PyEnum):
    PRIVATE = "private"
    PUBLIC = "public"

class Contract(Base):

    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str]
    owner_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(
        ENUM(
            Status,
            values_callable=lambda x: [i.value for i in x]
        ),
        server_default=Status.PUBLIC.value
    )
    file_path: Mapped[str]
    tg_file_id: Mapped[str | None]

    owner: Mapped['User'] = relationship(back_populates="contracts")
    contract_details: Mapped['ContractDetails'] = relationship(back_populates="contract")
