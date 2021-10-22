"""
"""
import configparser
import logging
from typing import Dict, Optional, Tuple, Any, List

from telegram import (
    Update, ChatMemberUpdated,
    ChatMember, ParseMode,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
)
from telegram.utils import helpers

from loggers import LogInstaller
from src.logic.entry_checker import EntryChecker


class ProctoringBot:
    __logger = LogInstaller.get_default_logger(__name__, logging.INFO)

    # states
    (
        ADD_USER,
        SELECT_ACTION,
        DESCRIBE_USER,
        SPECIFY_ATTRIBUTE,
        TYPE,
        STOP,
        SHOW
    ) = map(chr, range(1, 8))
    END = ConversationHandler.END

    # keys
    (
        ATTRIBUTES,
        CURRENT_ATTRIBUTE,
        USER_ID,
        INFO,
        GROUP,
        SUBGROUP,
        NAME,
        REPEATED_START,
        ERROR
    ) = map(chr, range(10, 19))

    def __init__(self, kick_min):
        self.__kick_min = kick_min

    def start_conversation(self, update: Update, context: CallbackContext) -> str:
        text = (
            'Для начала работы необходимо указать персональную информацию. '
            'Пожалуйста, зарегистрируйтесь.'
        )
        keyboard = ProctoringBot._get_inline_keyboard_markup([
            {'Зарегистрироваться': self.ADD_USER},
            {'Посмотреть информацию о себе': self.END}
        ])

        if context.user_data.get(self.REPEATED_START):
            update.callback_query.answer()
            update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
        else:
            update.message.reply_text(
                'Привет! Я бот Сергей)'
            )
            update.message.reply_text(text=text, reply_markup=keyboard)

        context.user_data[self.REPEATED_START] = False
        return self.SELECT_ACTION

    def add_user(self, update: Update, context: CallbackContext) -> str:
        context.user_data[self.USER_ID] = str(update.effective_user.id)
        text = 'Хорошо, укажите информацию о себе.'
        keyboard = ProctoringBot._get_inline_keyboard_markup([{
            'Указать информацию': self.INFO
        }])

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

        return self.DESCRIBE_USER

    def show_user_info(self, update: Update, context: CallbackContext) -> str:
        def get_info(user_data: Dict[str, Any]) -> str:
            user_id = user_data.get(self.USER_ID)
            print(user_id)
            if not user_id and not user_data[user_id]:
                return '\nВы не зарегестрированы.'

            user_info = user_data[user_id]
            text = ''
            text += f"\nФИО: {user_info.get(self.NAME, '-')}, Группа: {user_info.get(self.GROUP, '-')}, " \
                    f"Подгруппа: {user_info.get(self.SUBGROUP, '-')}"

            return text

        text_info = f"Информация:{get_info(context.user_data)}"
        keyboard = ProctoringBot._get_inline_keyboard_markup([{
            'Назад': self.END
        }])
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text_info, reply_markup=keyboard)
        context.user_data[self.REPEATED_START] = True

        return self.SHOW

    def stop_conversation(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text('Вы закончили.')

        return self.END

    def end_conversation(self, update: Update, context: CallbackContext) -> int:
        update.callback_query.answer()
        text = 'До скорой встречи.'
        update.callback_query.edit_message_text(text=text)

        return self.END

    def select_attribute(self, update: Update, context: CallbackContext) -> str:
        user_data = context.user_data
        keyboard = ProctoringBot._get_inline_keyboard_markup([{
            'ФИО': self.NAME,
            'Группа': self.GROUP,
            'Подгруппа': self.SUBGROUP,
            'Назад': self.END
        }])

        if user_data.get(self.REPEATED_START):
            if user_data.get(self.ERROR):
                text = user_data[self.ERROR]
                del user_data[self.ERROR]
            else:
                text = 'Отлично! Выберите другой параметр.'
            update.message.reply_text(text=text, reply_markup=keyboard)
        else:
            user_data[self.ATTRIBUTES] = {}
            if user_data.get(self.ERROR):
                text = user_data[self.ERROR]
                del user_data[self.ERROR]
            else:
                text = 'Выберите параметр.'

            update.callback_query.answer()
            update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

        user_data[self.REPEATED_START] = False
        return self.SPECIFY_ATTRIBUTE

    def request_attribute(self, update: Update, context: CallbackContext) -> str:
        context.user_data[self.CURRENT_ATTRIBUTE] = update.callback_query.data
        text = 'Хорошо, расскажите.'

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text)

        return self.TYPE

    def save_attribute(self, update: Update, context: CallbackContext) -> str:
        user_data = context.user_data
        text = update.message.text

        if user_data[self.CURRENT_ATTRIBUTE] == self.NAME and not EntryChecker.is_name_correct(text):
            user_data[self.ERROR] = 'Неверный ввод. Повторите.'

        user_data[self.ATTRIBUTES][user_data[self.CURRENT_ATTRIBUTE]] = text
        user_data[self.REPEATED_START] = True

        return self.select_attribute(update, context)

    def end_describing(self, update: Update, context: CallbackContext) -> int:
        user_data = context.user_data
        user_id = user_data[self.USER_ID]
        if not user_data.get(user_id):
            user_data[user_id] = []
        user_data[user_id].append(user_data[self.ATTRIBUTES])

        user_data = context.user_data
        user_data[self.REPEATED_START] = True
        self.start_conversation(update, context)

        return self.END

    def stop_describing(self, update: Update, context: CallbackContext) -> str:
        update.message.reply_text('Хорошо, пока.')

        return self.STOP

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
        was_member = ProctoringBot._define_status(old_status, old_is_member)
        is_member = ProctoringBot._define_status(new_status, new_is_member)

        return was_member, is_member

    def _set_timer(self, update: Update, context: CallbackContext, job_context: Optional[object], due: int) -> None:

        def alarm(context: CallbackContext) -> None:
            job = context.job
            update.effective_chat.send_message(
                text=f'{job.context[self.NAME]}, '
                     f'Вы не зарегистрировались!',
                parse_mode=ParseMode.HTML)
            context.bot.ban_chat_member(job.context[self.INFO], job.context[self.USER_ID])

        try:
            context.job_queue.run_once(alarm, due * 60, context=job_context, name=job_context[self.NAME])
        except (IndexError, ValueError):
            pass

    def _service_new_chat_member(self, update: Update, context: CallbackContext, member_name: str, cause_name: str):
        bot = context.bot
        url = helpers.create_deep_linked_url(bot.username, 'so-cool')

        update.effective_chat.send_message(
            f"{member_name} был добавлен {cause_name}.",
            parse_mode=ParseMode.HTML
        )
        update.effective_chat.send_message(
            f"Приветствуем! Пожалуйста, пройдите регистрацию в течение {EntryChecker.to_minutes_str_format(due)}.",
            reply_markup=InlineKeyboardMarkup.from_button(InlineKeyboardButton(text="Пройти!", url=url))
        )

        job_context = {
            self.NAME: member_name,
            self.USER_ID: update.chat_member.new_chat_member.user.id,
            self.INFO: update.effective_chat.id
        }
        self._set_timer(update, context, job_context, self.__kick_min)

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

    @staticmethod
    def _get_inline_keyboard_markup(buttons: List[Dict[str, str]]) -> InlineKeyboardMarkup:
        keyboards = []
        keyboard_group = []
        for group in buttons:
            for key in group:
                keyboard_group.append(InlineKeyboardButton(text=key, callback_data=str(group.get(key))))
            keyboards.append(keyboard_group)
            keyboard_group = []

        return InlineKeyboardMarkup(keyboards)
