"""
"""
from typing import Optional, Tuple

from telegram import ChatMember, ChatMemberUpdated, Update, ParseMode
from telegram.ext import CallbackContext
from telegram.utils import helpers

from src.data.user_data_manager import UserDataManager
from src.callee.keyboard_builder import KeyboardBuilder
from src.logic.entry_checker import EntryChecker
from src.user_data.spreadsheet_handler import SpreadsheetHandler


class RegistrationExpectationCallee:
    def __init__(self, ssh: SpreadsheetHandler, kick_min):
        self._ssh = ssh
        self._kick_min = kick_min
        self._udm = UserDataManager()
        self._rkb = KeyboardBuilder()

    @staticmethod
    def _define_status(status, is_member) -> bool:
        return (
            status
            in [
                ChatMember.MEMBER,
                ChatMember.CREATOR,
                ChatMember.ADMINISTRATOR,
            ]
            or (status == ChatMember.RESTRICTED and is_member is True)
        )

    @staticmethod
    def _extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
        status_change = chat_member_update.difference().get('status')
        old_is_member, new_is_member = chat_member_update.difference().get('is_member', (None, None))

        if status_change is None:
            return None

        old_status, new_status = status_change
        was_member = RegistrationExpectationCallee._define_status(old_status, old_is_member)
        is_member = RegistrationExpectationCallee._define_status(new_status, new_is_member)

        return was_member, is_member

    def _set_timer(self, update: Update, context: CallbackContext, job_context: Optional[object], due: int) -> None:
        username = self._udm.get_username(job_context)

        def alarm(context: CallbackContext) -> None:
            username = self._udm.get_username(job_context)
            if self._ssh.get_student_by_username(username) != {}:
                update.effective_chat.send_message(
                    text=f'{self._udm.get_user_alias(job_context)}, '
                         f'спасибо за регистрацию!',
                    parse_mode=ParseMode.HTML)
            else:
                update.effective_chat.send_message(
                    text=f'{self._udm.get_user_alias(job_context)}, '
                         f'Вы не зарегистрировались!',
                    parse_mode=ParseMode.HTML)
                context.bot.ban_chat_member(
                    self._udm.get_chat_id(job_context), self._udm.get_user_id(job_context)
                )

        try:
            context.job_queue.run_once(alarm, due * 60, context=job_context, name=username)
        except (IndexError, ValueError):
            pass

    def _service_new_chat_member(self, update: Update, context: CallbackContext, member_name: str, cause_name: str):
        user_data = context.user_data
        bot = context.bot
        url = helpers.create_deep_linked_url(bot.username, 'so-cool')

        update.effective_chat.send_message(
            f"{member_name} был добавлен {cause_name}.",
            parse_mode=ParseMode.HTML
        )

        username = update.chat_member.new_chat_member.user.username

        if self._ssh.get_student_by_username(username) == {}:
            update.effective_chat.send_message(
                f"Привет! Пожалуйста, пройдите регистрацию в течение "
                f"{EntryChecker.to_minutes_str_format(self._kick_min)}.",
                reply_markup=KeyboardBuilder().get_single_inline_keyboard_markup("Пройти!", url)
            )

            user_id = update.chat_member.new_chat_member.user.id
            self._udm.set_user_id(user_data, user_id)
            self._udm.set_username(user_data, member_name)
            user_data[self._udm.get_username(user_data)] = self._udm.get_user_id(user_data)

            job_context = {}
            self._udm.set_user_alias(job_context, member_name)
            self._udm.set_username(job_context, username)
            self._udm.set_user_id(job_context, user_id)
            self._udm.set_chat_id(job_context, update.effective_chat.id)

            self._set_timer(update, context, job_context, self._kick_min)

    def _service_left_chat_member(self, update: Update, context: CallbackContext, member_name: str, cause_name: str):
        update.effective_chat.send_message(
            f"{member_name} был исключён {cause_name}.",
            parse_mode=ParseMode.HTML,
        )

    def greet_chat_members(self, update: Update, context: CallbackContext) -> None:
        result = self._extract_status_change(update.chat_member)
        if result is None:
            return

        was_member, is_member = result
        cause_name = update.chat_member.from_user.mention_html()
        member_name = update.chat_member.new_chat_member.user.mention_html()
        if not was_member and is_member:
            self._service_new_chat_member(update, context, member_name, cause_name)
        elif was_member and not is_member:
            self._service_left_chat_member(update, context, member_name, cause_name)
