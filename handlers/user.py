from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from data.models import User
from data.repositories import ITelegramUserRepository, UserNotFound
from handlers.main import ConversationHandler
from keyboards import (register_confirmation_kb, return_to_main_kb,
                       share_phone_number_kb)
from locales import (ASK_PHONE_NUMBER, PHONE_NUMBER_SAVED, REGISTER,
                     REGISTER_CONFIRMATION, RETURN_TO_MAIN)
from utils import NotActualNumber, UserValidator

from .handler import Handler

if TYPE_CHECKING:
    from aiogram import Router
    from aiogram.fsm.context import FSMContext
    from aiogram.types import CallbackQuery, Message


class UserRegistrationForm(StatesGroup):
    phone_number = State()
    role = State()
    company_tin = State()


class UserHandler(Handler):

    def __init__(
        self,
        user_repository: "ITelegramUserRepository",
        user_validator: "UserValidator",
    ):

        if not isinstance(user_repository, ITelegramUserRepository):
            raise TypeError(
                "repository should be "
                + "instance of 'ITelegramUserRepository"
                + f" not {type(user_repository).__name__}"
            )

        if not isinstance(user_validator, UserValidator):
            raise TypeError(
                "user_validator should be "
                + "instance of 'UserValidator"
                + f" not {type(user_validator).__name__}"
            )

        self.user_repository = user_repository
        self.user_validator = user_validator

    def register_handlers(self, router: Router) -> None:
        """
        Registers all handlers to given router object.
        :param router - required
        """
        router.message.register(self.authenticate, CommandStart())
        router.callback_query.register(self.confirm_registration, F.data == REGISTER)
        router.message.register(
            self.process_phone_number, UserRegistrationForm.phone_number
        )

    async def authenticate(
        self,
        message: Message,
        state: FSMContext,
        conv_handler: ConversationHandler,
    ) -> None:
        """
        Checks the user registration status.
        If user has permission, it will give access main menu.
        Otherwise, redirects to registration.
        """

        user_id = message.from_user.id  # type: ignore

        try:
            current_user: User = self.user_repository.get_user_by_id(tg_user_id=user_id)

            await state.update_data(current_user=current_user)

            await conv_handler.cmd_start(message=message, state=state)
        except UserNotFound:
            await message.answer(
                text=REGISTER_CONFIRMATION, reply_markup=register_confirmation_kb()
            )

    async def confirm_registration(
        self, callback: "CallbackQuery", state: "FSMContext"
    ):
        await state.set_state(UserRegistrationForm.phone_number)

        await callback.message.delete()  # type: ignore
        await callback.message.answer(  # type: ignore
            text=ASK_PHONE_NUMBER, reply_markup=share_phone_number_kb()
        )

    async def process_phone_number(self, message: "Message", state: "FSMContext"):
        try:
            phone_number = self.user_validator.ensure_user_shared_own_contact(
                message=message
            )
            # await state.set_state(UserRegistrationForm.role)
            await state.update_data(phone_number=phone_number)

            user = message.from_user

            tg_user = User(
                id=user.id,  # type: ignore
                first_name=user.first_name,  # type: ignore
                last_name=user.last_name,  # type: ignore
                username=user.username,  # type: ignore
                phone_number=phone_number,
            )

            await message.answer(PHONE_NUMBER_SAVED, reply_markup=ReplyKeyboardRemove())
            await message.answer(RETURN_TO_MAIN, reply_markup=return_to_main_kb())
            # user

            self.user_repository.create_user(tg_user=tg_user)

        except NotActualNumber as e:
            await message.answer(str(e))


def register_user_handlers(
    router: "Router",
    user_repository: "ITelegramUserRepository",
    user_validator: "UserValidator",
):
    user_handler = UserHandler(
        user_repository=user_repository, user_validator=user_validator
    )
    user_handler.register_handlers(router=router)
