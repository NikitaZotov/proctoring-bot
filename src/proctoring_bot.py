"""
"""
import logging
from typing import Dict, Optional, Tuple, Any

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
from logic.entry_checker import EntryChecker
from src.data.keyboards import KeyboardBuilder


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

    # buttons
    (
        ATTRIBUTES,
        CURRENT_ATTRIBUTE,
        USER_ID,
        ID_NAME,
        REPEATED_START,
        ERROR
    ) = map(chr, range(10, 16))

    # attrs keys
    INFO = 'Информация'
    NAME = 'ФИО'
    GROUP = 'Группа'
    SUBGROUP = 'Подгруппа'
    OK = 'Хорошо'

    def __init__(self, kick_min):
        self.__kick_min = kick_min

    def get_primary_keyboard(self):
        return KeyboardBuilder.get_inline_keyboard_markup([
            {'Зарегистрироваться': self.ADD_USER},
            {'Посмотреть информацию о себе': self.SHOW}
        ])

    def get_info_request_text(self):
        return f'{self.OK}, укажите информацию о себе.'

    def get_info_request_keyboard(self):
        return KeyboardBuilder.get_inline_keyboard_markup([{
            'Указать информацию': self.INFO
        }])

    def get_ok_request_keyboard(self):
        return KeyboardBuilder.get_inline_keyboard_markup([{
            self.OK: self.END
        }])

    def get_select_attribute_keyboard(self):
        return KeyboardBuilder.get_inline_keyboard_markup(
            [
                {
                    self.NAME: self.NAME,
                    self.GROUP: self.GROUP,
                    self.SUBGROUP: self.SUBGROUP
                },
                {
                    'Подтвердить': self.END
                }
            ]
        )

    def _get_user_info(self, user_attrs):
        return f"\n{self.NAME}: {user_attrs.get(self.NAME, '-')}" \
               f"\n{self.GROUP}: {user_attrs.get(self.GROUP, '-')}" \
               f"\n{self.SUBGROUP}: {user_attrs.get(self.SUBGROUP, '-')}"

    def _update_callback(self, user_data, value: bool):
        user_data[self.REPEATED_START] = value

    def _is_updated_callback(self, user_data):
        return user_data.get(self.REPEATED_START)

    def _is_error_occurred(self, user_data):
        return user_data.get(self.ERROR)

    def _get_error(self, user_data):
        error = user_data[self.ERROR]
        del user_data[self.ERROR]
        return error

    def _set_error(self, user_data, value):
        user_data[self.ERROR] = value

    def _set_user_id(self, user_data, user_id: int):
        user_data[self.USER_ID] = str(user_id)

    def _get_user_id(self, user_data):
        return user_data.get(self.USER_ID)

    def _set_user_id_name(self, user_data, id_name: str):
        user_data[self.ID_NAME] = id_name

    def _get_user_id_name(self, user_data):
        return user_data.get(self.ID_NAME)

    def _set_user_attrs(self, user_data, other):
        user_data[self.ATTRIBUTES] = other

    def _get_user_attrs(self, user_data):
        return user_data.get(self.ATTRIBUTES)

    def _set_user(self, user_data, data):
        user_data[self._get_user_id(user_data)] = data

    def _set_cur_user_attr_key(self, user_data, data):
        user_data[self.CURRENT_ATTRIBUTE] = data

    def _get_cur_user_attr_key(self, user_data):
        return user_data.get(self.CURRENT_ATTRIBUTE)

    def _set_cur_user_attr(self, user_data, data):
        user_data[self.ATTRIBUTES][self._get_cur_user_attr_key(user_data)] = data

    def _get_user_attrs_by_id(self, user_data):
        return user_data.get(self._get_user_id(user_data))

    def _get_user_attrs_by_id_name(self, user_data, id_name):
        return user_data.get(user_data.get(id_name))

    def start_conversation(self, update: Update, context: CallbackContext) -> str:
        bot_data = context.bot_data
        keyboard = self.get_primary_keyboard()

        if self._is_updated_callback(bot_data):
            if self._is_error_occurred(bot_data):
                text = self._get_error(bot_data)
            else:
                text = 'Я Вас знаю. Вы зарегистрированы.'
            update.callback_query.answer()
            update.callback_query.edit_message_text(
                text=text, reply_markup=keyboard
            )
        else:
            update.message.reply_text(
                'Привет! Я бот Сергей)'
            )
            text = (
                'Для начала работы необходимо указать персональную информацию. '
                'Пожалуйста, зарегистрируйтесь.'
            )
            update.message.reply_text(
                text=text, reply_markup=keyboard
            )

        self._update_callback(bot_data, True)
        return self.SELECT_ACTION

    def add_user(self, update: Update, context: CallbackContext) -> str:
        user_data = context.user_data
        self._set_user_id(user_data, update.effective_user.id)
        self._set_user_id_name(user_data, update.effective_user.username)
        user_data[self._get_user_id_name(user_data)] = self._get_user_id(user_data)

        text = self.get_info_request_text()
        keyboard = self.get_info_request_keyboard()

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

        return self.DESCRIBE_USER

    def show_user_info(self, update: Update, context: CallbackContext) -> str:
        user_data = context.user_data

        def get_info() -> str:
            user_attrs = self._get_user_attrs_by_id(user_data)

            if not user_attrs:
                return '\nВы не зарегистрированы.'

            return self._get_user_info(user_attrs)

        text_info = f"{self.INFO}:\n{get_info()}"

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text_info, reply_markup=self.get_ok_request_keyboard())

        self._update_callback(user_data, True)
        return self.SHOW

    def show_concrete_user_info(self, update: Update, context: CallbackContext) -> str:
        user_data = context.user_data

        def get_info(id_name: str) -> str:
            user_attrs = self._get_user_attrs_by_id_name(user_data, id_name)

            if not user_attrs:
                return '\nЭтот пользователь не зарегистрирован.'

            return self._get_user_info(user_attrs)

        text_info = f"Информация о пользователе:\n{get_info(context.args[0][1:])}"
        update.effective_chat.send_message(text=text_info)

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
        keyboard = self.get_select_attribute_keyboard()

        if self._is_updated_callback(user_data):
            if self._is_error_occurred(user_data):
                text = self._get_error(user_data)
            else:
                text = 'Отлично! Выберите другой параметр.'
            update.message.reply_text(text=text, reply_markup=keyboard)
        else:
            self._set_user_attrs(user_data, {})
            if self._is_error_occurred(user_data):
                text = self._get_error(user_data)
            else:
                text = 'Выберите параметр.'

            update.callback_query.answer()
            update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

        self._update_callback(user_data, False)
        return self.SPECIFY_ATTRIBUTE

    def request_attribute(self, update: Update, context: CallbackContext) -> str:
        self._set_cur_user_attr_key(context.user_data, update.callback_query.data)
        text = f'{self.OK}, расскажите.'

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text)

        return self.TYPE

    def save_attribute(self, update: Update, context: CallbackContext) -> str:
        user_data = context.user_data
        text = update.message.text

        if self._get_cur_user_attr_key(user_data) == self.NAME \
                and not EntryChecker.is_name_correct(text):
            self._set_error(user_data, 'Данные не корректны. Повторите.')
        else:
            self._set_cur_user_attr(user_data, text)

        self._update_callback(user_data, True)
        return self.select_attribute(update, context)

    def end_describing(self, update: Update, context: CallbackContext) -> int:
        user_data = context.user_data
        user_id = self._get_user_id(user_data)
        if user_id:
            self._set_user(user_data, self._get_user_attrs(user_data))

        if not (user_data.get(self.NAME) and user_data.get(self.GROUP) and user_data.get(self.SUBGROUP)):
            self._set_error(user_data, 'Вы не были зарегистрированы, так как не всё рассказали о себе.')

        self._update_callback(user_data, True)
        self.start_conversation(update, context)

        return self.END

    def stop_describing(self, update: Update, context: CallbackContext) -> str:
        update.message.reply_text(f'{self.OK}, до встречи.')

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
                text=f'{job.context[self.ID_NAME]}, '
                     f'Вы не зарегистрировались!',
                parse_mode=ParseMode.HTML)
            context.bot.ban_chat_member(job.context[self.INFO], job.context[self.USER_ID])

        try:
            context.job_queue.run_once(alarm, due * 60, context=job_context, name=job_context[self.ID_NAME])
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
        update.effective_chat.send_message(
            f"Привет! Пожалуйста, пройдите регистрацию в течение "
            f"{EntryChecker.to_minutes_str_format(self.__kick_min)}.",
            reply_markup=KeyboardBuilder.get_single_inline_keyboard_markup("Пройти!", url)
        )

        user_id = update.chat_member.new_chat_member.user.id
        self._set_user_id(user_data, user_id)
        self._set_user_id_name(user_data, member_name)
        user_data[self._get_user_id_name(user_data)] = self._get_user_id(user_data)

        job_context = {
            self.ID_NAME: member_name,
            self.USER_ID: id,
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
