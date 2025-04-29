from aiogram import F
from typing import TYPE_CHECKING

from locales.uz import NO_DOCUMENTS


from .handler import Handler
from data.repositories import IDocumentRepository, DocumentNotFound
from keyboards import list_of_templates

from locales import ( MY_DOCUMENTS,
    NO_TEMPLATES, CREATE_DOCUMENT,
    SELECT_TEMPLATE
)

if TYPE_CHECKING:
    from aiogram import Router
    from aiogram.types import Message, CallbackQuery
    from aiogram.fsm.context import FSMContext
    from data.models import Document
    from re import Match


    

class DocumentHandler(Handler):
    def __init__(self, document_repository: 'IDocumentRepository'):
        super().__init__()

        if not isinstance(document_repository, IDocumentRepository):
            raise TypeError(
                "document_repository should be instance" + 
               f" of 'IdocumentRepository' not {type(document_repository).__name__}"
            )
        
        self._repo = document_repository

    
    def register_handlers(self, router: 'Router'):
        
        router.callback_query.register(self.my_documents, F.data==MY_DOCUMENTS)
        router.callback_query.register(self.my_templates, F.data==CREATE_DOCUMENT)
        

    
    async def my_documents(self, callback: 'CallbackQuery', state: 'FSMContext') -> None:
        try:
            user_id = callback.from_user.id
            all_documents: list['Document'] = self._repo.get_all(owner_id=user_id)
            await callback.answer()

        except NotImplementedError:
            await callback.message.answer(NO_DOCUMENTS) # type: ignore


    async def my_templates(self, callback: 'CallbackQuery') -> None:
        try:
            user_id = callback.from_user.id
            templates: list['Document'] = self._repo.get_all(
                owner_id=user_id, is_template=True
            )
            
            await callback.message.edit_text( # type: ignore
                text=SELECT_TEMPLATE,
                reply_markup=list_of_templates(templates)
            )
            await callback.answer()

        except DocumentNotFound:
            await callback.message.answer(NO_TEMPLATES)  # type: ignore




def register_document_handler(
    router: 'Router', 
    document_repository: 'IDocumentRepository'
) -> None:
    document_handler = DocumentHandler(document_repository=document_repository)

    document_handler.register_handlers(router=router)

