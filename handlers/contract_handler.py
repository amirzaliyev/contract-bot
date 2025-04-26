from aiogram import F
from aiogram.filters import Command
from typing import TYPE_CHECKING

from .handler import Handler
from data.repositories import ContractRepository
from locales import NO_CONTRACTS, MY_CONTRACTS

if TYPE_CHECKING:
    from aiogram import Router
    from aiogram.types import Message
    from aiogram.fsm.context import FSMContext

class ContractHandler(Handler):
    def __init__(self, contract_repository: 'ContractRepository'):
        super().__init__()

        if not isinstance(contract_repository, ContractRepository):
            raise TypeError(
                "contract_repository should be instance" + 
               f" of 'ContractRepository' not {type(contract_repository).__name__}"
            )
        
        self._repo = contract_repository

    
    def register_handlers(self, router: 'Router'):
        
        router.callback_query.register(self.my_contracts, F.data==MY_CONTRACTS)
        
    
    async def my_contracts(self, message: 'Message', state: 'FSMContext'):
        try:
            all_contracts = self._repo.get_all_contracts()

        except NotImplementedError():
            await message.answer(NO_CONTRACTS)


