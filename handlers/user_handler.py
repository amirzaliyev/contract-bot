from aiogram import F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from typing import TYPE_CHECKING

from locales import (
    CREATE_DOCUMENT, 
    REGISTER, REGISTER_CONFIRMATION, 
    ASK_PHONE_NUMBER, PHONE_NUMBER_SAVED,
    SELECT_TEMPLATE
)
from keyboards import (
    create_contract_kb, 
    register_confirmation_kb, 
    share_phone_number_kb
)
from .handler import Handler
from data.repositories import ITelegramUserRepository, UserNotFound
from data.models import User
from utils import UserValidator, NotActualNumber

if TYPE_CHECKING:
    from aiogram import Router
    from aiogram.types import Message, CallbackQuery
    from aiogram.fsm.context import FSMContext

class UserRegistrationForm(StatesGroup):
    phone_number = State()
    role = State()
    company_tin = State()



class UserHandler(Handler):

    def __init__(self, tg_user_repository: 'ITelegramUserRepository', user_validator: 'UserValidator'):

        if not isinstance(tg_user_repository, ITelegramUserRepository):
            raise TypeError(
                "repository should be "  + 
                "instance of 'ITelegramUserRepository" +
                f" not {type(tg_user_repository).__name__}"
            )
        
        if not isinstance(user_validator, UserValidator):
            raise TypeError(
                "user_validator should be "  + 
                "instance of 'UserValidator" +
                f" not {type(user_validator).__name__}"
            )
        
        self.tg_user_repository = tg_user_repository
        self.user_validator = user_validator


    def register_handlers(self, router: 'Router') -> None:
        """
        Registers all handlers to given router object.
        :param router - required
        """
        # router.callback_query.register(self.authenticate, F.data == CREATE_CONTRACT)
        router.callback_query.register(self.confirm_registration, F.data == REGISTER)
        router.message.register(self.process_phone_number, UserRegistrationForm.phone_number)


    async def authenticate(
        self,
        callback: 'CallbackQuery', 
        state: 'FSMContext'
    ) -> None:
        """
        Checks the user registration status. 
        If user has permission, it will give access main menu.
        Otherwise, redirects to registration.
        """

        user_id = callback.from_user.id

        try:
            current_user: User = self.tg_user_repository.get_user_by_id(tg_user_id=user_id)

            await state.update_data(current_user=current_user)

            await callback.message.edit_text(SELECT_TEMPLATE) # type: ignore



        except UserNotFound:
            await callback.message.edit_text( # type: ignore
                text = REGISTER_CONFIRMATION,
                reply_markup = register_confirmation_kb()
            )
            await callback.answer()


    async def confirm_registration(
        self,
        callback: 'CallbackQuery',
        state: 'FSMContext'
    ):
        await state.set_state(UserRegistrationForm.phone_number)

        await callback.message.delete() # type: ignore
        await callback.message.answer( # type: ignore
            text = ASK_PHONE_NUMBER,
            reply_markup = share_phone_number_kb()
        )


    async def process_phone_number(
        self,
        message: 'Message',
        state: 'FSMContext'
    ):
        try:
            phone_number = self.user_validator.ensure_user_shared_own_contact(
                message = message
            )
            # await state.set_state(UserRegistrationForm.role)
            await state.update_data(phone_number=phone_number)

            user = message.from_user

            tg_user = User(
                id=user.id,  # type: ignore
                first_name = user.first_name, # type: ignore
                last_name = user.last_name, # type: ignore
                username = user.username, # type: ignore
                phone_number = phone_number
            )

            await message.answer(PHONE_NUMBER_SAVED, reply_markup=ReplyKeyboardRemove())

            # user


            self.tg_user_repository.create_user(tg_user=tg_user)

        except NotActualNumber as e:
            await message.answer(str(e))
        


def register_user_handlers(
        router: 'Router', 
        tg_user_repository: 'ITelegramUserRepository',
        user_validator: 'UserValidator'
    ):
    user_handler = UserHandler(
        tg_user_repository=tg_user_repository,
        user_validator=user_validator
    )
    user_handler.register_handlers(router=router)
