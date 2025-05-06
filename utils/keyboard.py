from __future__ import annotations
from abc import ABC
from typing import Generic, TypeVar, Type, List, Optional, Union, Any, TYPE_CHECKING

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

BuilderType = TypeVar("BuilderType", InlineKeyboardBuilder, ReplyKeyboardBuilder)


class KeyboardService(Generic[BuilderType], ABC):
    """Creates keyboard"""

    def __init__(self, builder_type: Type[BuilderType]) -> None:
        if not issubclass(builder_type, (InlineKeyboardBuilder, ReplyKeyboardBuilder)):
            raise ValueError(f"Builder type {builder_type} are not allowed here")
        self._builder_type = builder_type

    def create_keyboard(
        self,
        buttons: List[dict],
        sizes: Optional[List[int]] = None,
        resize_keyboard: bool = True,
        **kwargs: Any,
    ) -> Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]:
        """
        Creates a keyboards

        :param buttons: One or more button kwargs
        :param sizes: Number of columns in rows if number of buttons are more
            than specified sizes, size[-1] will be used for rest of the rows
            default: [3]
        :param resize_keyboard: if true, keyboard will be dynamically resized

        :returns: InlineKeyboardMarkup or ReplyKeyboardMarkup
        """
        if sizes is None:
            sizes = [3]

        builder = self._builder_type()
        builder.adjust(*sizes)

        for btn_kwargs in buttons:
            if "text" not in btn_kwargs:
                raise ValueError("Each button must have a 'text' key")

            if isinstance(builder, InlineKeyboardBuilder):
                if not any(
                    key in btn_kwargs
                    for key in {"callback_data", "url", "switch_inline_query"}
                ):
                    raise ValueError(
                        "Inline keyboard buttons must include at least one"
                        + " of 'callback_data', 'url', or 'switch_inline_query'"
                    )

            builder.button(**btn_kwargs)

        return builder.as_markup(resize_keyboard=resize_keyboard, **kwargs)


class InlineKeyboardService(KeyboardService[InlineKeyboardBuilder]):
    """
    Inline keyboard service inherits all methods from generic service
    """

    def __init__(self) -> None:
        super().__init__(builder_type=InlineKeyboardBuilder)

    if TYPE_CHECKING:
        def create_keyboard(
            self,
            buttons: List[dict],
            sizes: Optional[List[int]] = None,
            resize_keyboard: bool = True,
            **kwargs: Any,
        ) -> InlineKeyboardMarkup:
            """Constructs an InlineKeyboardMarkup"""
            ...


class ReplyKeyboardService(KeyboardService[ReplyKeyboardBuilder]):
    """
    Reply keyboard service inherits all methods from generic service
    """

    def __init__(self) -> None:
        super().__init__(builder_type=ReplyKeyboardBuilder)

    if TYPE_CHECKING:

        def create_keyboard(
            self,
            buttons: List[dict],
            sizes: Optional[List[int]] = None,
            resize_keyboard: bool = True,
            **kwargs: Any,
        ) -> ReplyKeyboardMarkup:
            """Construct an ReplyKeyboardMarkup"""
            ...
