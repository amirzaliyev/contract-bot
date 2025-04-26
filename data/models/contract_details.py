from sqlalchemy import TEXT, ForeignKey, BIGINT
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING

from .base import Base
from .user import User

if TYPE_CHECKING:
    from .contract import Contract

class ContractDetails(Base):
    __tablename__ = "contract_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    variable_name: Mapped[str]
    description: Mapped[str] = mapped_column(TEXT, nullable=False)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"))

    contract: Mapped['Contract'] = relationship(back_populates="contract_details")
