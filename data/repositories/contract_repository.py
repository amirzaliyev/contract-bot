from abc import ABC, abstractmethod

from data.models import Contract

class IContractRepository(ABC):

    @abstractmethod
    def get_all_contracts(self, user_id: int) -> list['Contract']:
        """
        Retrieves all contracts available contracts to the user

        :param user_id Telegram user id

        :returns list[Contract]
        """
        pass


    @abstractmethod
    def get_contract_by_id(self, user_id: int, contract_id: int) -> 'Contract':
        """
        Retrieves contract by contract id

        :param user_id Telegram user id
        :param contract_id Contract id
        
        :returns Contract

        Raises
            ContractNotFound error if there is no contract with given contract_id
        """
        pass


    @abstractmethod
    def create_contract(self, contract: 'Contract') -> None:
        """
        Creates a new contract and saves it to database

        :param contract - Contract object

        :returns
        """
        pass

    @abstractmethod
    def update_contract(self, contract: 'Contract') -> None:
        """
        Updates an existing contract and saves it to database

        :param contract - Contract object

        :returns
        """
        pass


class ContractRepository(IContractRepository):
    
    def get_all_contracts(self, user_id: int) -> list['Contract']:
        raise NotImplementedError()
    

    def get_contract_by_id(self, user_id: int, contract_id: int) -> 'Contract':
        raise NotImplementedError()
    

    def create_contract(self, contract: 'Contract') -> None:
        raise NotImplementedError()
    

    def update_contract(self, contract: 'Contract') -> None:
        raise NotImplementedError()