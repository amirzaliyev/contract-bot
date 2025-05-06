from typing import TYPE_CHECKING
from aiogram import F

from data.repositories import IDocumentRepository, DocumentNotFound
from keyboards import list_of_templates
from locales import (
    NO_DOCUMENTS,
    MY_DOCUMENTS,
)
from .handler import Handler

if TYPE_CHECKING:
    from aiogram import Router
    from aiogram.types import Message, CallbackQuery
    from aiogram.fsm.context import FSMContext
    from data.models import Document


class DocumentHandler(Handler):
    def __init__(self, document_repository: "IDocumentRepository"):
        super().__init__()

        if not isinstance(document_repository, IDocumentRepository):
            raise TypeError(
                "document_repository should be instance"
                + f" of 'IdocumentRepository' not {type(document_repository).__name__}"
            )

        self._repo = document_repository

    def register_handlers(self, router: "Router"):

        router.callback_query.register(self.my_documents, F.data == MY_DOCUMENTS)

    async def my_documents(
        self, callback: "CallbackQuery", state: "FSMContext"
    ) -> None:
        try:
            user_id = callback.from_user.id
            all_documents: list["Document"] = self._repo.get_all(owner_id=user_id)
            await callback.answer()

        except NotImplementedError:
            await callback.message.answer(NO_DOCUMENTS)  # type: ignore


def register_document_handler(
    router: "Router", document_repository: "IDocumentRepository"
) -> None:
    document_handler = DocumentHandler(document_repository=document_repository)

    document_handler.register_handlers(router=router)
