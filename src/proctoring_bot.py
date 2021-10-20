"""
"""
import configparser
from typing import Dict, Optional

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)


class ProctoringBot:
    __states = {
        'choosing': 0,
        'typing_reply': 1,
        'typing_choice': 2
    }

    __keys = [
        ['ФИО', 'Группа'],
        ['Подгруппа'],
        ['Закрыть']
    ]

    def __init__(self):
        self.__markup = ReplyKeyboardMarkup(self.__keys)

    @staticmethod
    def get_student_info(user_data: Dict[str, str]) -> str:
        info = [f'{key} - {value}' for key, value in user_data.items()]
        return "\n".join(info).join(['\n', '\n'])

    def init_conversation(self, update: Update, context: CallbackContext) -> int:
        user_id = context.user_data["id"]
        update.message.reply_text(
            "Доброго времени суток!",
            reply_markup=self.__markup,
            reply_to_message_id=user_id
        )

        return self.__states['choosing']

    def regular_choice(self, update: Update, context: CallbackContext) -> int:
        text = update.message.text
        context.user_data['choice'] = text
        update.message.reply_text(f'Введите Ваше {text}.')

        return self.__states['typing_reply']

    def custom_choice(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text('Укажите дополнительную информацию.')

        return self.__states['typing_choice']

    def receive_information(self, update: Update, context: CallbackContext) -> int:
        user_data = context.user_data
        text = update.message.text
        category = user_data['choice']
        user_data[category] = text
        del user_data['choice']

        return self.__states['choosing']

    @staticmethod
    def done(update: Update, context: CallbackContext) -> int:
        user_data = context.user_data
        if 'choice' in user_data:
            del user_data['choice']

        update.message.reply_text(
            f"Информация о Вас: {ProctoringBot.get_student_info(user_data)}",
            reply_markup=ReplyKeyboardRemove(),
        )

        user_data.clear()
        return ConversationHandler.END

    def start(self):
        config = configparser.ConfigParser()
        config.read("settings.ini")

        updater = Updater('2092452318:AAFuVGp-Mx2fe6_NrN0-jTsA43n_M8vA0TU')
        dispatcher = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.init_conversation)],
            states={
                self.__states['choosing']: [
                    MessageHandler(
                        Filters.regex('^(ФИО|Группа|Подгруппа)$'), self.regular_choice
                    ),
                    MessageHandler(Filters.regex('^Дополнительные данные$'), self.custom_choice),
                ],
                self.__states['typing_choice']: [
                    MessageHandler(
                        Filters.text & ~(Filters.command | Filters.regex('^Информация указана.$')), self.regular_choice
                    )
                ],
                self.__states['typing_reply']: [
                    MessageHandler(
                        Filters.text & ~(Filters.command | Filters.regex('^Информация указана.$')),
                        self.receive_information,
                    )
                ],
            },
            fallbacks=[MessageHandler(Filters.regex('^Информация указана.$'), self.done)],
        )
        dispatcher.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
