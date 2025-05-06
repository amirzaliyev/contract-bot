from typing import TYPE_CHECKING

from utils import InlineKeyboardService, ReplyKeyboardService
from locales import YES, NO, ADD_TEMPLATE

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup
    from data.models import Document


inline_kb_service = InlineKeyboardService()
reply_kb_service = ReplyKeyboardService()

text = "text"
callback_data = "callback_data"
request_contact = "request_contact"


def list_of_templates(templates: list["Document"]) -> "InlineKeyboardMarkup":
    buttons = []
    add_template = {text: ADD_TEMPLATE, callback_data: ADD_TEMPLATE}

    buttons.append(add_template)
    for template in templates:
        btn_kwargs = {
            text: template.file_name,
            callback_data: f"template_{template.id}",
        }
        buttons.append(btn_kwargs)

    return inline_kb_service.create_keyboard(buttons=buttons, resize_keyboard=True)


def doc_create_confirmation() -> "InlineKeyboardMarkup":
    btns = [{text: YES, callback_data: YES}, {text: NO, callback_data: NO}]
    return inline_kb_service.create_keyboard(buttons=btns, resize_keyboard=True)
