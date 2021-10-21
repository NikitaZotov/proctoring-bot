import configparser

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler
)

from proctoring_bot import ProctoringBot


class BotStarter:
    @staticmethod
    def start():
        bot = ProctoringBot()

        config = configparser.ConfigParser()
        config.read("settings.ini")
        updater = Updater(config['Bot']['token'])
        dispatcher = updater.dispatcher

        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', bot.init_conversation)],
            states={
                bot.states['choosing']: [
                    MessageHandler(
                        Filters.regex('^(ФИО|Группа|Подгруппа)$'), bot.regular_choice
                    )
                ],
                bot.states['typing_choice']: [
                    MessageHandler(
                        Filters.text & ~(Filters.command | Filters.regex('^Информация указана.$')), bot.regular_choice
                    )
                ],
                bot.states['typing_reply']: [
                    MessageHandler(
                        Filters.text & ~(Filters.command | Filters.regex('^Информация указана.$')),
                        bot.receive_information,
                    )
                ],
            },
            fallbacks=[MessageHandler(Filters.regex('^Информация указана.$'), bot.done)],
        )
        dispatcher.add_handler(conversation_handler)

        updater.start_polling()
        updater.idle()
