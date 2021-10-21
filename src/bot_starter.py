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
            entry_points=[CommandHandler('start', bot.greet)],
            states={
                bot.states['choosing']: [
                    MessageHandler(
                        Filters.regex('^ФИО$'), bot.get_name
                    )
                ],
                bot.states['get_info']: [
                    MessageHandler(
                        Filters.regex('^Группа$'), bot.get_group
                    )
                ],
                bot.states['get_info']: [
                    MessageHandler(
                        Filters.regex('^Подгруппа$'), bot.get_subgroup
                    )
                ],
                bot.states['keyboard']: [
                    MessageHandler(
                        Filters.text, bot.show_keyboard
                    )
                ],
                bot.states['reading_info']: [
                    MessageHandler(
                        Filters.text & ~Filters.command, bot.done
                    )
                ],
            },
            fallbacks=[MessageHandler(Filters.regex('^Информация указана.$'), bot.done)],
        )
        dispatcher.add_handler(conversation_handler)

        updater.start_polling()
        updater.idle()
