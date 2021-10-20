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
        'typing_reply': 1,
        'typing_choice': 2
    }

    __keys = [
        ['ФИО', 'Группа'],
        ['Подгруппа'],
        ['Закрыть']
    ]

    @staticmethod
    def get_student_info(user_data: Dict[str, str]) -> str:
        info = [f'{key} - {value}' for key, value in user_data.items()]
        return "\n".join(info).join(['\n', '\n'])

    def init_conversation(self, update: Update, context: CallbackContext) -> int:
        update.message.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Доброго времени суток!",
            reply_markup=ReplyKeyboardMarkup(self.__keys),
        )
        return self.states['choosing']

    def regular_choice(self, update: Update, context: CallbackContext) -> int:
        text = update.message.text
        context.user_data['choice'] = text
        update.message.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Введите Ваше {text}'
        )
        return self.states['typing_reply']

    def receive_information(self, update: Update, context: CallbackContext) -> int:
        user_data = context.user_data
        text = update.message.text
        category = user_data['choice']
        user_data[category] = text
        del user_data['choice']
        return self.states['choosing']

    @staticmethod
    def done(update: Update, context: CallbackContext) -> int:
        user_data = context.user_data
        if 'choice' in user_data:
            del user_data['choice']

        update.message.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Информация о Вас: {ProctoringBot.get_student_info(user_data)}",
            reply_markup=ReplyKeyboardRemove(),
        )

        user_data.clear()
        return ConversationHandler.END
