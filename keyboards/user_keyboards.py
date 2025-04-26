from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from locales import CREATE_CONTRACT, REGISTER, SHARE_PHONE_NUMBER, MY_CONTRACTS

def create_contract_kb() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard = [
            [
                InlineKeyboardButton(
                    text = CREATE_CONTRACT,
                    callback_data = CREATE_CONTRACT
                ),
                InlineKeyboardButton(
                    text=MY_CONTRACTS,
                    callback_data=MY_CONTRACTS
                )
            ]
        ]
    )


def register_confirmation_kb() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard = [
            [
                InlineKeyboardButton(
                    text = REGISTER,
                    callback_data = REGISTER
                )
            ]
        ]
    )

def share_phone_number_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard = [
            [
                KeyboardButton(
                    text = SHARE_PHONE_NUMBER,
                    request_contact = True
                )
            ]
        ],
        resize_keyboard = True
    )