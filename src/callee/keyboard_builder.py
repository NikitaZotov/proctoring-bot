"""
"""
from typing import List, Dict

from telegram import InlineKeyboardMarkup, InlineKeyboardButton


class KeyboardBuilder:
    def get_inline_keyboard_markup(self, buttons: List[Dict[str, str]]) -> InlineKeyboardMarkup:
        keyboards = []
        keyboard_group = []
        for group in buttons:
            for key in group:
                keyboard_group.append(InlineKeyboardButton(text=key, callback_data=str(group.get(key))))
            keyboards.append(keyboard_group)
            keyboard_group = []

        return InlineKeyboardMarkup(keyboards)

    def get_single_inline_keyboard_markup(self, name: str, url: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup.from_button(InlineKeyboardButton(name, url=url))
