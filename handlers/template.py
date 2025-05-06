from typing import Dict, List, TYPE_CHECKING
from aiogram import F
from aiogram.types import FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import and_f


from data.models.document import Document
from data.repositories import ITemplateFieldRepository
from data.repositories.document_repository import DocumentNotFound, IDocumentRepository
from handlers.handler import Handler
from keyboards import doc_create_confirmation, list_of_templates
from utils.doc_editor import DocumentService
from locales import (
    CREATE_DOCUMENT,
    NO_DETAILS,
    SUMMARY,
    CREATE_DOC,
    YES,
    PROCESSING_DOC,
    SELECT_TEMPLATE,
    NO_TEMPLATES,
)
from .handler import Handler

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
        template_field_repository: "ITemplateFieldRepository",
        doc_repository: "IDocumentRepository",
        doc_editor: "DocumentService",
    ):
        if not isinstance(template_field_repository, ITemplateFieldRepository):
            raise TypeError(
                "template_field_repository should be an instance of 'ITemplateFieldRepository',"
                + f"not {type(template_field_repository).__name__}"
            )

        if not isinstance(doc_repository, IDocumentRepository):
            raise TypeError(
                "doc_repository should be instance of 'IDocumentRepository', not"
                + f"\n {type(doc_repository).__name__}"
            )

        if not isinstance(doc_editor, DocumentService):
            raise TypeError(
                "doc_editor should be instance of 'DocumentService', not"
                + f"\n {type(doc_editor).__name__}"
            )

        self._temp_field_repo = template_field_repository
        self._doc_repo = doc_repository
        self._doc_editor = doc_editor

    def register_handlers(self, router: "Router") -> None:
        router.callback_query.register(self.my_templates, F.data == CREATE_DOCUMENT)
        router.callback_query.register(
            self.create_from_template,
            F.data.regexp(r"^template_(\d+)$").as_("template_id"),
        )
        router.message.register(self.fill_out_template, FillTemplate.filling_template)
        router.message.register(self.show_summary, FillTemplate.confirm_data)
        router.callback_query.register(
            self.create_doc, and_f(FillTemplate.create_doc, F.data == YES)
        )

    async def my_templates(self, callback: "CallbackQuery") -> None:
        try:
            user_id = callback.from_user.id
            templates: List["Document"] = self._doc_repo.get_all(
                owner_id=user_id, is_template=True
            )
            print(templates)

            await callback.message.edit_text(  # type: ignore
                text=SELECT_TEMPLATE, reply_markup=list_of_templates(templates)
            )

        except DocumentNotFound:
            await callback.message.answer(NO_TEMPLATES)  # type: ignore

    async def create_from_template(
        self, callback: "CallbackQuery", state: "FSMContext", template_id: "Match[str]"
    ) -> None:
        try:
            await callback.answer()
            template_id_int = int(template_id.group(1))
            await state.update_data(template_id=template_id_int)

            # Extract required fields from the template
            fields = self._extract_required_fields(template_id=template_id_int)

            await state.set_state(FillTemplate.filling_template)

            if not fields:
                await callback.message.edit_text(NO_DETAILS)  # type: ignore
                await state.clear()
                return

            # Prepare fields that is required to be filled
            await state.update_data(
                fields=fields,
                current_field_index=0,
                filled_data={},
            )

            await callback.message.edit_text(  # type: ignore
                text=fields[0]["description"]
            )

        except ValueError as e:
            await callback.message.edit_text(str(e))  # type: ignore

    def _extract_required_fields(self, template_id: int) -> List[Dict[str, str]]:
        fields = self._temp_field_repo.get_all(document_id=template_id)

        required_fields = []
        for field in fields:
            field_in_dict = {}
            field_in_dict["field_name"] = field.field_name
            field_in_dict["description"] = field.description

            required_fields.append(field_in_dict)

        return required_fields

    async def fill_out_template(self, message: "Message", state: "FSMContext") -> None:

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
            await self.show_summary(message=message, state=state)
            await state.update_data(filled_data=filled_data)

        else:
            await state.update_data(
                current_field_index=current_index, filled_data=filled_data
            )

            await message.answer(text=fields[current_index]["description"])

    async def show_summary(self, message: "Message", state: "FSMContext") -> None:
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
            text=summary + CREATE_DOC, reply_markup=doc_create_confirmation()
        )

    async def create_doc(self, callback: "CallbackQuery", state: "FSMContext") -> None:
        data = await state.get_data()
        filled_data = data["filled_data"]
        await callback.message.edit_text(text=PROCESSING_DOC)  # type: ignore
        await state.clear()

        # todo try catch block FileNotFoundError

        user_id = callback.from_user.id

        output_file_path, document_id = self._doc_editor.fill_template(
            user_id=user_id,
            template_id=data["template_id"],
            context=filled_data,
        )

        await self.send_doc(
            callback.message, output_file_path, doc_id=document_id, user_id=user_id  # type: ignore
        )

    async def send_doc(
        self, message: "Message", doc_path: str, doc_id: int, user_id: int
    ) -> None:
        await message.delete()
        file = FSInputFile(doc_path)
        uploaded_file = await message.answer_document(file)
        file_id = uploaded_file.document.file_id  # type: ignore
        self._doc_repo.update_document(
            document=Document(id=doc_id, tg_file_id=file_id, owner_id=user_id)
        )


def register_template_handler(
    router: "Router",
    template_field_repository: "ITemplateFieldRepository",
    doc_repository: "IDocumentRepository",
    doc_editor: "DocumentService",
) -> None:
    template_handler = TemplateHandler(
        template_field_repository=template_field_repository,
        doc_repository=doc_repository,
        doc_editor=doc_editor,
    )
    template_handler.register_handlers(router=router)
