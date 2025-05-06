from __future__ import annotations
import os
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional
from aiogram.fsm.state import State, StatesGroup
from aiogram import F

from data.repositories import IDocumentRepository, ITemplateFieldRepository
from data.models import Document, TemplateField
from handlers import Handler
from locales import (
    ADD_TEMPLATE,
    SEND_TEMPLATE,
    FILE_SAVED,
    ADD_REQUIRED_FIELDS,
    FIELD_FORMAT,
    ERR_SAVE_FILE,
    FIELD_FORMAT_INCORRECT,
)
from config import TEMP_DIR, BOT_DIR


if TYPE_CHECKING:
    from aiogram import Router, Bot
    from aiogram.types import Message, CallbackQuery
    from aiogram.fsm.context import FSMContext


class AddTemplate(StatesGroup):
    download_file = State()
    add_fields = State()


class AddNewTemplateHandler(Handler):

    def __init__(
        self,
        doc_repository: IDocumentRepository,
        temp_field_repository: ITemplateFieldRepository,
    ):
        if not isinstance(doc_repository, IDocumentRepository):
            raise TypeError(
                "doc_repository should be an instance of 'IDocumentRepository'"
                + f" not {type(doc_repository).__name__}"
            )

        if not isinstance(temp_field_repository, ITemplateFieldRepository):
            raise TypeError(
                "temp_field_repository should be an instance of 'ITemplateFieldRepository'"
                + f" not {type(temp_field_repository).__name__}"
            )

        self._repo = doc_repository
        self._temp_field_repo = temp_field_repository

    def register_handlers(self, router: Router):
        router.callback_query.register(
            self.start_template_adding, F.data == ADD_TEMPLATE
        )
        router.message.register(self.download_template, AddTemplate.download_file)
        router.message.register(self.get_required_fields, AddTemplate.add_fields)

    async def start_template_adding(
        self, callback: CallbackQuery, state: FSMContext
    ) -> None:
        await callback.answer()

        await callback.message.edit_text(text=SEND_TEMPLATE)  # type: ignore
        await state.set_state(AddTemplate.download_file)

    async def download_template(
        self, message: Message, bot: Bot, state: FSMContext
    ) -> None:
        doc = message.document
        file_info = await bot.get_file(doc.file_id) # type: ignore
        file_name = doc.file_name # type: ignore
        await state.update_data(file_name=file_name)

        file_path = file_info.file_path
        destination_dir = Path(TEMP_DIR, f"{message.from_user.id}") #type: ignore
        os.makedirs(destination_dir, exist_ok=True)

        destination_path = Path(destination_dir, file_name) # type: ignore
        await state.update_data(destination=destination_path) # type: ignore

        await bot.download_file(file_path, destination_path) # type: ignore
        await message.reply(
            FILE_SAVED + "\n" + ADD_REQUIRED_FIELDS + "\n" + FIELD_FORMAT
        )

        await state.set_state(AddTemplate.add_fields)

    async def get_required_fields(self, message: Message, state: FSMContext):
        try:
            fields = self._validate_temp_fields(text=message.text) #type: ignore
            doc_id = await self.save_template(message, state)
            if doc_id:
                self._save_required_fields(temp_id=doc_id, fields=fields)

        except ValueError:
            await message.reply(FIELD_FORMAT_INCORRECT + "\n" + FIELD_FORMAT)

    async def save_template(self, message: Message, state: FSMContext) -> Optional[int]:
        data = await state.get_data()
        destination = data["destination"]
        file_relative_path = Path(destination).relative_to(BOT_DIR).as_posix()
        file_name = data["file_name"].rsplit(".", maxsplit=1)[0]

        document = Document(
            file_name=file_name,
            owner_id=message.from_user.id,  # type: ignore
            file_path=file_relative_path,
            is_template=True,
        )
        try:
            doc = self._repo.create_document(document=document)
            return doc.id

        except Exception as e:
            await message.answer(str(e))
            await message.answer(ERR_SAVE_FILE)

    def _save_required_fields(self, temp_id: int, fields: Dict) -> None:
        current_index = 1
        for key, desc in fields.items():
            tf = TemplateField(
                field_name=key,
                description=desc,
                field_order=current_index,
                template_id=temp_id,
            )

            self._temp_field_repo.create_template_field(template_field=tf)
            current_index += 1

    def _validate_temp_fields(self, text: str) -> Dict[str, str]:
        cmd_list = text.split("\n")

        fields = {}

        for substr in cmd_list:
            field_pairs = substr.split("-", maxsplit=1)

            if len(field_pairs) != 2:
                raise ValueError("Invalid format")

            key = field_pairs[0].strip()
            desc = field_pairs[1].strip()

            if not key or not desc:
                raise ValueError("Field name and its description are mandatory")

            fields[key] = desc

        return fields


def register_add_template_handler(
    router: Router,
    doc_repository: IDocumentRepository,
    temp_field_repository: ITemplateFieldRepository,
) -> None:
    handler = AddNewTemplateHandler(
        doc_repository=doc_repository, temp_field_repository=temp_field_repository
    )
    handler.register_handlers(router=router)
