from sqlalchemy import TEXT, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from .base import Base

class TemplateField(Base):
    __tablename__ = "template_fields"

    id: Mapped[int] = mapped_column(primary_key=True)
    field_name: Mapped[str]
    description: Mapped[str] = mapped_column(TEXT, nullable=False)
    detail_order: Mapped[int]
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))

