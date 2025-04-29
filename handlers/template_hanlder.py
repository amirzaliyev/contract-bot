from typing import Dict, List, TYPE_CHECKING
from pathlib import Path
from datetime import datetime
from aiogram import F
from aiogram.types import FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import and_f



from data.repositories import ITemplateFieldsRepository
from handlers.handler import Handler
from locales.uz import NO_DETAILS, SUMMARY

from .handler import Handler
from data.repositories import DocumentNotFound
from keyboards import doc_create_confirmation
from utils.doc_editor import fill_template
from config import DOCS_DIR, TEMPLATES_DIR
from locales import (
    CREATE_DOC, 
    YES, PROCESSING_DOC,
)

if TYPE_CHECKING:
    from aiogram import Router
    from aiogram.types import Message, CallbackQuery
    from aiogram.fsm.context import FSMContext
    from re import Match
    
    
class FillTemplate(StatesGroup):
    filling_template = State()
    confirm_data = State()
    create_doc = State()
    
    
    
class TemplateHandler(Handler):
    
    def __init__(
        self, 
        template_field_repository: 'ITemplateFieldsRepository'
    ):
        if not isinstance(template_field_repository, ITemplateFieldsRepository):
            raise TypeError(
                "template_field_repository should be an instance of 'ITemplateFieldRepository'," +
                f"not {type(template_field_repository).__name__}"
            )
            
        self._repo = template_field_repository
    
    def register_handlers(self, router: 'Router') -> None:
        router.callback_query.register(
            self.create_from_template, 
            F.data.regexp(r"^template_(\d+)$").as_("template_id")
        )
        router.message.register(
            self.fill_out_template, 
            FillTemplate.filling_template
        )
        router.message.register(
            self.show_summary,
            FillTemplate.confirm_data
        )
        router.callback_query.register(
            self.create_doc, and_f(
                FillTemplate.create_doc, F.data==YES
            )
        )
    
    
    async def create_from_template(
        self, callback: 'CallbackQuery',
        state: 'FSMContext', 
        template_id: 'Match[str]'
    ) -> None:
        try: 
            await callback.answer()
            template_id_int = int(template_id.group(1))
            
            # Extract required fields from the template
            fields = self._extract_required_fields(
                template_id=template_id_int
            )
            
            await state.set_state(FillTemplate.filling_template)
            
            if not fields:
                await callback.message.answer(NO_DETAILS) # type: ignore
            
            # Prepare fields that is required to be filled
            await state.update_data(
                fields=fields,
                current_field_index=0,
                filled_data={},
            )
            
            await callback.message.edit_text(  # type: ignore
                text=fields[0]["description"]
            )
        
        except (ValueError, DocumentNotFound) as e:
            await callback.message.edit_text(str(e))  # type: ignore


    def _extract_required_fields(self, template_id: int) -> List[Dict[str, str]]:
        fields = self._repo.get_all(
            document_id=template_id
        )
        
        required_fields = []
        for field in fields:
            field_in_dict = {}
            field_in_dict['field_name'] = field.field_name
            field_in_dict['description'] = field.description
            
            required_fields.append(field_in_dict)        
                
        return required_fields

    async def fill_out_template(
        self, message: 'Message', 
        state: 'FSMContext'
    ) -> None:
            
        data = await state.get_data()    
        current_index = data["current_field_index"]
        fields = data["fields"]
        current_field = fields[current_index]
        filled_data = data["filled_data"]
        
        # Save current input
        field_name = current_field["field_name"]
        filled_data[field_name] = message.text
        
        # Increment current index
        current_index += 1
        
        if len(fields) <= len(filled_data):
            # Show summary
            await self.show_summary(
                message=message, 
                state=state
            )
            await state.update_data(filled_data=filled_data)
            
        else:
            await state.update_data(
                current_field_index = current_index,
                filled_data=filled_data
            )
            
            await message.answer(
                text=fields[current_index]["description"]
            )
            
    
    async def show_summary(self, message: 'Message', state: 'FSMContext') -> None:
        data = await state.get_data()
        fields = data["fields"]
        filled_data = data["filled_data"]
        summary = SUMMARY
        
        for field in fields:
            field_name = field["field_name"]
            summary += f"\n{field['description']}: {filled_data[field_name]}"
            
        await state.set_state(FillTemplate.create_doc)
        
        # Send confirmation
        await message.answer(
            text=summary + CREATE_DOC,
            reply_markup=doc_create_confirmation()
        )


    async def create_doc(
        self, callback: 'CallbackQuery',
        state: 'FSMContext'
    ) -> None:
        data = await state.get_data()
        filled_data = data["filled_data"]
        await callback.message.edit_text(  # type: ignore
            text=PROCESSING_DOC
        )
        await state.clear()

        template = Path.joinpath(TEMPLATES_DIR, "template2.docx")
        output_file = Path.joinpath(DOCS_DIR, f"Doc {datetime.now().timestamp()}.docx")
        fill_template(template, output_path=output_file, context=filled_data)

        await self.send_doc(callback.message, output_file)  # type: ignore


    async def send_doc(self, message: 'Message', doc_path) -> None:
        await message.delete()
        file = FSInputFile(doc_path)
        await message.answer_document(file)

    

def register_template_handler(
    router: 'Router', 
    template_field_repository: 'ITemplateFieldsRepository'
) -> None:
    template_handler = TemplateHandler(template_field_repository=template_field_repository)
    template_handler.register_handlers(router=router)