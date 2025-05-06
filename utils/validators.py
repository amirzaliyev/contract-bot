from aiogram.types import Message

class NotActualNumber(Exception):
    """Raised when a contact is not the user's own phone number."""


class UserValidator:

    """
    Contains methods for validating user-submitted Telegram contact data.
    """

    def ensure_user_shared_own_contact(self, message: Message) -> str:
        """
        Ensures the user shared their own contact using the Telegram button.
        
        Args:
            message (Message): Incoming Telegram message
        
        Returns:
            str: The user's phone number

        Raises:
            NotActualNumber: If the contact was not shared via Telegram's request_contact,
                             or it's not the user's own number.
        """

        if not message.contact:
            raise NotActualNumber(
                "❌ Please use the *Share Contact* button to send your own number."
            )

        if message.contact.user_id != message.from_user.id: # type: ignore
            raise NotActualNumber(
                "❌ You must share *your own* contact, not someone else's."
            )

        return message.contact.phone_number

