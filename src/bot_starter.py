"""
"""
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler, ChatMemberHandler, CallbackQueryHandler
)

from proctoring_bot import ProctoringBot


class BotStarter:
    START = 'start'
    STOP = 'stop'

    def __init__(self, token):
        self.bot = ProctoringBot()
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher

    def get_description_conversation_handler(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.bot.select_attribute, pattern='^' + str(self.bot.INFO) + '$')
            ],
            states={
                self.bot.SPECIFY_ATTRIBUTE: [
                    CallbackQueryHandler(self.bot.request_attribute, pattern='^(?!' + str(self.bot.END) + ').*$')
                ],
                self.bot.TYPE: [
                    MessageHandler(Filters.text & ~Filters.command, self.bot.save_attribute)
                ],
            },
            fallbacks=[
                CallbackQueryHandler(self.bot.end_describing, pattern='^' + str(self.bot.END) + '$'),
                CommandHandler(self.STOP, self.bot.stop_describing),
            ],
            map_to_parent={
                self.bot.END: self.bot.DESCRIBE_USER,
                self.bot.STOP: self.bot.STOP
            },
        )

    def get_main_conversation_handler(self) -> ConversationHandler:
        selection_handlers = [
            CallbackQueryHandler(self.bot.show_user_info, pattern='^' + str(self.bot.SHOW) + '$'),
            CallbackQueryHandler(self.bot.add_user, pattern='^' + str(self.bot.ADD_USER) + '$'),
        ]
        return ConversationHandler(
            entry_points=[CommandHandler(self.START, self.bot.start_conversation)],
            states={
                self.bot.SHOW: [CallbackQueryHandler(self.bot.start_conversation, pattern='^' + str(self.bot.END) + '$')],
                self.bot.SELECT_ACTION: selection_handlers,
                self.bot.DESCRIBE_USER: [self.get_description_conversation_handler()],
                self.bot.STOP: [CommandHandler(self.START, self.bot.start_conversation)],
            },
            fallbacks=[CommandHandler(self.STOP, self.bot.stop_conversation)],
        )

    def get_chat_member_handler(self):
        return ChatMemberHandler(self.bot.greet_chat_members, ChatMemberHandler.CHAT_MEMBER)

    def handle(self):
        self.dispatcher.add_handler(self.get_main_conversation_handler())
        self.dispatcher.add_handler(self.get_chat_member_handler())

        self.updater.start_polling()
        self.updater.idle()
