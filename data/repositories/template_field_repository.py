from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

from data.models import TemplateField

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker


class TemplateFieldNotFound(Exception):
    pass


class ITemplateFieldRepository(ABC):

    @abstractmethod
    def get_all(self, template_id: int) -> List["TemplateField"]:
        """
        Retrieves all the template document required fields by document id

        Args:
            template_id: int Template 'Document' id

        Returns:
            List['TemplateFields'] - list of TemplateField objects

        Raises:
            TemplateFieldNotFound - if there is no field for given document id.
        """
        pass

    @abstractmethod
    def get_template_field_by_id(self, template_id: int) -> "TemplateField":
        """
        Retrieves template field by its id

        Args:
            template_id (int): TemplateField id

        Returns:
            TemplateField object

        Raises:
            TemplateFieldNotFound - if there is no template field for given field id
        """
        pass

    @abstractmethod
    def create_template_field(self, template_field: "TemplateField") -> TemplateField:
        """
        Creates a new template field

        Args:
            template_field (TemplateField): TemplateField object
        """
        pass

    @abstractmethod
    def update_template_field(self, template_field: "TemplateField") -> None:
        """
        Updates an existing template field

        Args:
            template_field (TemplateField): TemplateField object
        """
        pass


class TemplateFieldRepository(ITemplateFieldRepository):

    def __init__(self, sessionmaker: "sessionmaker[Session]"):

        # todo validate sessionmaker

        self._session = sessionmaker

    def get_all(self, template_id: int) -> List[TemplateField]:

        with self._session() as session:
            results = session.query(TemplateField).filter_by(template_id=template_id)

        if not results:
            raise TemplateFieldNotFound(
                f"There is no template field record for id {template_id}"
            )

        fields = []

        for field in results:
            fields.append(field)

        return fields

    def get_template_field_by_id(self, template_id: int) -> TemplateField:
        raise NotImplementedError("This method should be overridden in a subclass")

    def create_template_field(self, template_field: TemplateField) -> TemplateField:
        with self._session() as session:
            session.add(template_field)
            session.commit()
            session.refresh(template_field)
            return template_field

    def update_template_field(self, template_field: TemplateField) -> None:
        raise NotImplementedError("This method should be overridden in a subclass")
