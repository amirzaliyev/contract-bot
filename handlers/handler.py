from abc import ABC, abstractmethod
from aiogram import Router



class Handler(ABC):
    
    @abstractmethod
    def register_handlers(router: Router) -> None:
        """
        Registers all handlers to given router
        
        :param - Router
        :returns 
        """
        pass