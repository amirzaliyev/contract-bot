from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from data.models import User

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker
    

class ITelegramUserRepository(ABC):

    @abstractmethod
    def get_all_users(self) -> list['User'] | list:
        """
        Returns:
            list[User] | list 
        """
        pass
    
    @abstractmethod 
    def get_user_by_id(self, tg_user_id: int) -> 'User':
        """
        Args:
            tg_user_id (int): Actual telegram user id

        Returns:
            User: User
        
        Exceptions:
            UserNotFound: if user not found
        """
        pass
    
    @abstractmethod
    def create_user(self, tg_user: 'User') -> 'User':
        """
        Args:
            tg_user (User): Telegram user
        
        Returns:
            User: Telegram user
        """
        pass
    
    @abstractmethod
    def update_user(self, tg_user: 'User') -> None:
        """
        Args:
            tg_user (User): Telegram user

        Returns: nothing
        """
        pass

    @abstractmethod
    def delete_user(self, tg_user_id: int) -> None:
        """
        Args:
            tg_user_id (int): Telegram user id

        Returns: nothing
        """
        pass

class UserNotFound(Exception):
    pass

class TelegramUserRepository(ITelegramUserRepository):

    def __init__(self, session: 'sessionmaker[Session]'):
        
        # todo session validation...

        self._session = session

    def get_all_users(self) -> list['User']:
        raise NotImplementedError()
    
    def get_user_by_id(self, tg_user_id: int) -> 'User':
        with self._session() as session:
            tg_user = session.get(User, tg_user_id)

            if not tg_user:
                raise UserNotFound(f"There is no user record with id: {tg_user_id}")
            
        return tg_user
    
    def create_user(self, tg_user: 'User') -> 'User':
        with self._session() as session:
            session.add(tg_user)

            session.commit()
        
        return tg_user
        
    def update_user(self, tg_user: 'User') -> None:
        raise NotImplementedError()
    
    def delete_user(self, tg_user_id: int) -> None:
        raise NotImplementedError()