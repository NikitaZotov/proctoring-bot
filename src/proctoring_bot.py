"""
"""
import logging

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler, ChatMemberHandler, CallbackQueryHandler
)

from src.callee.registration_expectation_callee import RegistrationExpectationCallee
from src.callee.registration_dialog_callee import RegistrationDialogCalle
from src.loggers import LogInstaller
from src.logic.spreadsheet_handler import SpreadsheetHandler


class ProctoringBot:
    START = 'start'
    STOP = 'stop'
    INFO = 'info'

    def __init__(self, token, kick_min, s_id):
        self._logger = LogInstaller.get_default_logger(__name__, logging.INFO)

        self._updater = Updater(token)
        self._dispatcher = self._updater.dispatcher

        ssh = SpreadsheetHandler(s_id, 'spreadsheet_token.json')
        ssh.create_spreadsheet(100, 8)
        self._rd_calle = RegistrationDialogCalle(ssh)
        self._re_calle = RegistrationExpectationCallee(ssh, kick_min)

    def get_description_conversation_handler(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    callback=self._rd_calle.select_attribute,
                    pattern='^' + str(self._rd_calle.SELECT_ATTRIBUTE) + '$'
                )
            ],
            states={
                self._rd_calle.SPECIFY_ATTRIBUTE: [
                    CallbackQueryHandler(
                        callback=self._rd_calle.request_attribute,
                        pattern='^(?!' + str(self._rd_calle.END) + ').*$'
                    )
                ],
                self._rd_calle.TYPE: [
                    MessageHandler(
                        filters=Filters.text & ~Filters.command,
                        callback=self._rd_calle.save_attribute
                    )
                ],
            },
            fallbacks=[
                CallbackQueryHandler(
                    callback=self._rd_calle.end_describing,
                    pattern='^' + str(self._rd_calle.END) + '$'
                ),
                CommandHandler(
                    command=self.STOP,
                    callback=self._rd_calle.stop_describing
                ),
            ],
            map_to_parent={
                self._rd_calle.END: self._rd_calle.SELECT_ACTION,
                self._rd_calle.STOP: self._rd_calle.STOP
            },
        )

    def get_chat_member_handler(self):
        return ChatMemberHandler(self._re_calle.greet_chat_members, ChatMemberHandler.CHAT_MEMBER)

    def get_main_conversation_handler(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[
                CommandHandler(
                    command=self.START,
                    callback=self._rd_calle.start_conversation
                )
            ],
            states={
                self._rd_calle.SHOW: [
                    CallbackQueryHandler(
                        callback=self._rd_calle.start_conversation,
                        pattern='^' + str(self._rd_calle.END) + '$'
                    )
                ],
                self._rd_calle.SELECT_ACTION: [
                    CallbackQueryHandler(
                        callback=self._rd_calle.show_user_info,
                        pattern='^' + str(self._rd_calle.SHOW) + '$'
                    ),
                    CallbackQueryHandler(
                        callback=self._rd_calle.add_user,
                        pattern='^' + str(self._rd_calle.ADD_USER) + '$'
                    )
                ],
                self._rd_calle.DESCRIBE_USER: [self.get_description_conversation_handler()],
                self._rd_calle.STOP: [
                    CommandHandler(
                        command=self.START,
                        callback=self._rd_calle.start_conversation
                    )
                ],
            },
            fallbacks=[
                CommandHandler(
                    command=self.INFO,
                    callback=self._rd_calle.show_concrete_user_info
                ),
                CommandHandler(
                    command=self.START,
                    callback=self._rd_calle.start_conversation
                )
            ],
        )

    def start(self):
        self._dispatcher.add_handler(self.get_main_conversation_handler())
        self._dispatcher.add_handler(self.get_chat_member_handler())

        self._updater.start_polling()
        self._updater.idle()
