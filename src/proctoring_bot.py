"""
"""
from typing import Dict

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
)


class ProctoringBot:
    states = {
        'choosing': 0,
        'keyboard': 1,
        'reading_info': 2,
        'get_info': 3
    }

    __keys = [
        ['ФИО', 'Группа'],
        ['Подгруппа'],
        ['Закрыть']
    ]

    @staticmethod
    def get_student_info(user_data: Dict[str, str]) -> str:
        info = [f'{key} - {value}' for key, value in user_data.items()]
        return '\n'.join(info).join(['\n', '\n'])

    def greet(self, update: Update, context: CallbackContext) -> int:
        update.message.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Доброго времени суток!',
            reply_markup=ReplyKeyboardMarkup([['ФИО']], one_time_keyboard=True),
        )
        return self.states['choosing']

    def get_name(self, update: Update, context: CallbackContext) -> int:
        update.message.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Введи имя'
        )
        context.user_data['key'] = 'Группа'
        return self.states['keyboard']

    def get_group(self, update: Update, context: CallbackContext) -> int:
        update.message.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Введи группу'
        )
        context.user_data['key'] = 'Подгруппа'
        return self.states['keyboard']

    def get_subgroup(self, update: Update, context: CallbackContext) -> int:
        update.message.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Введи подгруппу'
        )
        return self.states['keyboard']

    def show_keyboard(self, update: Update, context: CallbackContext) -> int:
        update.message.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Ок!',
            reply_markup=ReplyKeyboardMarkup([[context.user_data['key']]], one_time_keyboard=True),
        )
        return self.states['get_info']

    @staticmethod
    def done(update: Update, context: CallbackContext) -> int:
        user_data = context.user_data
        if 'choice' in user_data:
            del user_data['choice']

        update.message.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Информация о Вас: {ProctoringBot.get_student_info(user_data)}',
            reply_markup=ReplyKeyboardRemove(),
        )

        user_data.clear()
        return ConversationHandler.END
