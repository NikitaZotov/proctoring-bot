"""
"""
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

from loggers import LogInstaller


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
    ) = map(chr, range(10, 18))

    def start_conversation(self, update: Update, context: CallbackContext) -> str:
        text = (
            'Для начала работы необходимо указать персональную информацию. '
            'Пожалуйста, зарегистрируйтесь.'
        )
        keyboard = ProctoringBot.get_inline_keyboard_markup([
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
        keyboard = ProctoringBot.get_inline_keyboard_markup([{
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
        keyboard = ProctoringBot.get_inline_keyboard_markup([{
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
        keyboard = ProctoringBot.get_inline_keyboard_markup([{
            'ФИО': self.NAME,
            'Группа': self.GROUP,
            'Подгруппа': self.SUBGROUP,
            'Назад': self.END
        }])

        if context.user_data.get(self.REPEATED_START):
            text = 'Отлично! Выберите другой параметр.'
            update.message.reply_text(text=text, reply_markup=keyboard)
        else:
            context.user_data[self.ATTRIBUTES] = {}
            text = 'Выберите параметр.'

            update.callback_query.answer()
            update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

        context.user_data[self.REPEATED_START] = False
        return self.SPECIFY_ATTRIBUTE

    def request_attribute(self, update: Update, context: CallbackContext) -> str:
        context.user_data[self.CURRENT_ATTRIBUTE] = update.callback_query.data
        text = 'Хорошо, расскажите.'

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text)

        return self.TYPE

    def save_attribute(self, update: Update, context: CallbackContext) -> str:
        user_data = context.user_data
        user_data[self.ATTRIBUTES][user_data[self.CURRENT_ATTRIBUTE]] = update.message.text

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
    def define_status(status, is_member) -> bool:
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
    def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
        status_change = chat_member_update.difference().get('status')
        old_is_member, new_is_member = chat_member_update.difference().get('is_member', (None, None))

        if status_change is None:
            return None

        old_status, new_status = status_change
        was_member = ProctoringBot.define_status(old_status, old_is_member)
        is_member = ProctoringBot.define_status(new_status, new_is_member)

        return was_member, is_member

    def greet_chat_members(self, update: Update, context: CallbackContext) -> None:
        result = self.extract_status_change(update.chat_member)
        if result is None:
            return

        was_member, is_member = result
        cause_name = update.chat_member.from_user.mention_html()
        member_name = update.chat_member.new_chat_member.user.mention_html()

        if not was_member and is_member:
            update.effective_chat.send_message(
                f"{member_name} был добавлен {cause_name}. Приветствуем!",
                parse_mode=ParseMode.HTML,
            )
        elif was_member and not is_member:
            update.effective_chat.send_message(
                f"{member_name} был исключён {cause_name}.",
                parse_mode=ParseMode.HTML,
            )

    @staticmethod
    def get_inline_keyboard_markup(buttons: List[Dict[str, str]]) -> InlineKeyboardMarkup:
        keyboards = []
        keyboard_group = []
        for group in buttons:
            for key in group:
                keyboard_group.append(InlineKeyboardButton(text=key, callback_data=str(group.get(key))))
            keyboards.append(keyboard_group)
            keyboard_group = []

        return InlineKeyboardMarkup(keyboards)
