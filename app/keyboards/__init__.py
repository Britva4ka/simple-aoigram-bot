import random

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from typing import Optional, List, Union

default_placeholder = [
    "What to choose? 🤔",
    "So many options 👀",
    "Tough choice! 🤯",
    "Time to decide! 💪",
    "The choice is yours! ✨",
    "So many options! 🤩",
    "Time to choose ⏳",
    "Which one to choose? 🤔",
    "They all look great! 😍",
    "Make a decision! 🚀",
    "What do you say? 💬",
    "What's your choice? 💭",
    "Think again 🧐",
    "So, what now? 🤷",
    "So many options! 🎉",
]


class BaseReplyMarkup:
    """
    Parent class for ReplyKeyboards
    """

    def _generate_markup(
        self,
        buttons: Optional[List[str]] = None,
        row_size: Optional[Union[int, List[int]]] = 2,
        placeholder: Optional[str] = None,
    ) -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        all_buttons = self.get_buttons_list_from_attributes()

        if buttons:
            all_buttons.extend(buttons if isinstance(buttons, list) else [buttons])

        self._add_buttons_to_builder(buttons_list=all_buttons, builder=builder)
        if isinstance(row_size, int):
            markup = builder.adjust(row_size, repeat=True).as_markup(
                resize_keyboard=True,
                input_field_placeholder=placeholder
                or random.choice(default_placeholder),
            )
        else:
            markup = builder.adjust(*row_size, repeat=True).as_markup(
                resize_keyboard=True,
                input_field_placeholder=placeholder
                or random.choice(default_placeholder),
            )
        return markup

    @staticmethod
    def _add_buttons_to_builder(
        buttons_list: List[str], builder: ReplyKeyboardBuilder
    ) -> None:
        for button in buttons_list:
            builder.add(KeyboardButton(text=button))

    def get_buttons_list_from_attributes(self) -> List[str]:
        attributes = vars(self.__class__)
        string_attributes = [
            value
            for key, value in attributes.items()
            if isinstance(value, str) and not key.startswith("__")
        ]
        return string_attributes

    def get(
        self,
        row_size: Optional[Union[int, List[int]]] = 2,
        placeholder: Optional[str] = None,
        buttons: Optional[List[str]] = None,
    ) -> ReplyKeyboardMarkup:
        return self._generate_markup(
            buttons=buttons, row_size=row_size, placeholder=placeholder
        )


class BaseInlineMarkup:
    def _generate_markup(
        self,
        buttons: Optional[List[Union[str, tuple]]] = None,
        row_size: Optional[Union[int, List[int]]] = 2,
    ) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        all_buttons = self._get_buttons_list_from_attributes()

        if buttons:
            if isinstance(buttons, list):
                all_buttons.extend(buttons)
            elif isinstance(buttons, str):
                all_buttons.append(buttons)

        self._add_buttons_to_builder(buttons_list=all_buttons, builder=builder)
        if isinstance(row_size, int):
            markup = builder.adjust(row_size, repeat=True).as_markup()
        else:
            markup = builder.adjust(*row_size, repeat=True).as_markup()
        return markup

    @staticmethod
    def _add_buttons_to_builder(
        buttons_list: List[Union[str, tuple]], builder: InlineKeyboardBuilder
    ) -> None:
        for button in buttons_list:
            if isinstance(button, str):
                builder.add(InlineKeyboardButton(text=button, callback_data=button))
            elif isinstance(button, tuple) and len(button) == 2:
                text, callback_data = button
                builder.add(
                    InlineKeyboardButton(text=text, callback_data=callback_data)
                )

    def _get_buttons_list_from_attributes(self) -> List[Union[str, tuple]]:
        attributes = vars(self.__class__)
        buttons_list = []
        for key, value in attributes.items():
            if not key.startswith("__"):
                if isinstance(value, str):
                    buttons_list.append(value)
                elif isinstance(value, tuple) and len(value) == 2:
                    buttons_list.append(value)
        return buttons_list

    def get(
        self,
        row_size: Optional[Union[int, List[int]]] = 2,
        buttons: Optional[List[Union[str, tuple]]] = None,
    ) -> InlineKeyboardMarkup:
        return self._generate_markup(buttons=buttons, row_size=row_size)
