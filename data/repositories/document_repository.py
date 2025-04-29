from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List
from sqlalchemy import or_

from data.models import Document

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker


class IDocumentRepository(ABC):

    @abstractmethod
    def get_all(self, owner_id: int, is_template: bool = False) -> List['Document']:
        """
        By default, retrieves all documents available documents to the user.
        If is_template is true, it will return all document templates available to user

        :param owner_id int - Telegram user id
        :param is_template Bool 

        :returns list[Document]
        """
        pass


    @abstractmethod
    def get_document_by_id(
        self,
        owner_id: int,
        document_id: int,
        is_template: bool = False
    ) -> 'Document':
        """
        By default, retrieves a document by document id.
        If is_template is true, it will return a template available to user

        :param owner_id int - Telegram user id
        :param document_id int - Document id
        :param is_template bool 
        
        :returns Document

        Raises
            DocumentNotFound error if there is no document that matches given requirements
        """
        pass


    @abstractmethod
    def create_document(self, document: 'Document') -> None:
        """
        Creates a new document and saves it to database

        :param document - Document object

        :returns
        """
        pass

    @abstractmethod
    def update_document(self, document: 'Document') -> None:
        """
        Updates an existing document and saves it to database

        :param document - Document object

        :returns
        """
        pass

class DocumentNotFound(Exception):
    pass

class DocumentRepository(IDocumentRepository):

    def __init__(self, session: 'sessionmaker[Session]'):

        # todo validate session

        self._session = session
    
    def get_all(self, owner_id: int, is_template: bool = False) -> List['Document']:
        
        with self._session() as session:
            documents = (
                session.query(Document).filter(
                    or_(Document.owner_id==owner_id, Document.status=='public'),
                    Document.is_template==is_template
                )
            )
            
        if not documents:
            raise DocumentNotFound(f"There is no document available to user")

        results = []

        for document in documents:
            results.append(document)
        
        return results

    def get_document_by_id(
        self,
        owner_id: int,
        document_id: int,
        is_template: bool = False
    ) -> 'Document':
        with self._session() as session:
            document = session.query(Document).filter_by(
                id=document_id, 
                owner_id=owner_id, 
                is_template=is_template
            ).one_or_none()
            
        if not document:
            raise DocumentNotFound(f"There is no document with id {document_id}")

        return document
    

    def create_document(self, document: 'Document') -> None:
        with self._session() as session:
            session.add(document)
            session.commit()
    

    def update_document(self, document: 'Document') -> None:
        raise NotImplementedError()