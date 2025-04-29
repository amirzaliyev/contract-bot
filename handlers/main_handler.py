import logging
import sys

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from .handler import Handler
from locales import WELCOME_MESSAGE
from keyboards import create_contract_kb

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout
)


class ConversationHandler(Handler):

    def register_handlers(self, router: 'Router') -> None:
        """
        Registers all handlers to given router object.
        :param router - required
        """
        router.message.register(self.cmd_start, CommandStart())
        router.message.register(self.cancel, Command("cancel"))
        logging.info("conversation handlers registered")

    async def cmd_start(self, message: 'Message', state: 'FSMContext') -> None:
        await message.answer(
            text=WELCOME_MESSAGE,
            reply_markup=create_contract_kb()
        )

    async def cancel(self, message: 'Message', state: 'FSMContext') -> None:
        """
        Allow user to cancel any action
        """

        current_state = await state.get_state()

        if current_state is None:
            return

        logging.info("Cancelling state %r", current_state)
        await state.clear()
        await message.answer(
            "Cancelled.",
            reply_markup=ReplyKeyboardRemove()
        )


def register_conversation_handler(
        router: 'Router'
):
    conv_handler = ConversationHandler()
    conv_handler.register_handlers(router=router)
