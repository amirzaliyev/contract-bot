from typing import TYPE_CHECKING

from locales import (CREATE_DOCUMENT, MY_DOCUMENTS, REGISTER, RETURN_TO_MAIN,
                     SHARE_PHONE_NUMBER)
from utils import InlineKeyboardService, ReplyKeyboardService

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

reply_kb_service = ReplyKeyboardService()
inline_kb_service = InlineKeyboardService()

text = "text"
callback_data = "callback_data"
request_contact = "request_contact"


def create_contract_kb() -> "InlineKeyboardMarkup":
    create_contract = {text: CREATE_DOCUMENT, callback_data: CREATE_DOCUMENT}
    my_contracts = {text: MY_DOCUMENTS, callback_data: MY_DOCUMENTS}
    kbs = [create_contract, my_contracts]
    size = [2]

    return inline_kb_service.create_keyboard(buttons=kbs, size=size)


def register_confirmation_kb() -> "InlineKeyboardMarkup":
    reg_confirmation = {text: REGISTER, callback_data: REGISTER}

    kbs = [reg_confirmation]
    return inline_kb_service.create_keyboard(buttons=kbs)


def share_phone_number_kb() -> "ReplyKeyboardMarkup":
    share_phone_num = {text: SHARE_PHONE_NUMBER, request_contact: True}

    kbs = [share_phone_num]

    return reply_kb_service.create_keyboard(buttons=kbs)


def return_to_main_kb() -> "InlineKeyboardMarkup":
    back_to_main = {text: RETURN_TO_MAIN, callback_data: RETURN_TO_MAIN}

    kbs = [back_to_main]

    return inline_kb_service.create_keyboard(buttons=kbs)
