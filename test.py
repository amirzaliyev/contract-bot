from __future__ import annotations
import asyncio
import logging
import sys
from typing import TYPE_CHECKING
from aiogram import F, Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from config import settings

if TYPE_CHECKING:
    from aiogram.types import Message, CallbackQuery

lovely_router = Router()


def reply_kb() -> ReplyKeyboardMarkup:
    btn = KeyboardButton(text="hello")

    return ReplyKeyboardMarkup(keyboard=[[btn]])


def inline_kb() -> InlineKeyboardMarkup:
    btn = InlineKeyboardButton(text="test me", callback_data="test me")

    return InlineKeyboardMarkup(inline_keyboard=[[btn]])


@lovely_router.message(CommandStart())
async def cmd_start_love(message: Message):
    """Sends love to the world"""
    await message.answer(
        "Hello world of testing and improving", reply_markup=reply_kb()
    )


@lovely_router.message(F.text == "hello")
async def foo(message: Message) -> None:
    """Responds to love"""
    await message.delete()
    await message.answer(text="hi", reply_markup=ReplyKeyboardRemove())
    await message.answer(
        text="I don't know it will work or not", reply_markup=inline_kb()
    )


async def main() -> None:
    bot = Bot(token=settings.BOT_TOKEN)

    dp = Dispatcher()

    dp.include_router(lovely_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
