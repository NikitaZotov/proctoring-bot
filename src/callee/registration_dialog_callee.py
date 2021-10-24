"""
"""
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from src.callee.keyboard_builder import KeyboardBuilder
from src.logic.entry_checker import EntryChecker
from src.data.user_data_manager import UserDataManager
from src.user_data.spreadsheet_handler import SpreadsheetHandler


class RegistrationKeyboardBuilder(KeyboardBuilder):
    # attrs keys
    INFO = 'Информация'
    FULL_NAME = 'ФИО'
    GROUP = 'Группа'
    SUBGROUP = 'Подгруппа'
    OK = 'Хорошо'

    def get_primary_keyboard_if_not_registered(self):
        return self.get_inline_keyboard_markup([
            {'Зарегистрироваться': RegistrationDialogCalle.ADD_USER},
            {'Посмотреть личную информацию': RegistrationDialogCalle.SHOW}
        ])

    def get_primary_keyboard_if_registered(self):
        return self.get_inline_keyboard_markup([
            {'Изменить данные о себе': RegistrationDialogCalle.ADD_USER},
            {'Посмотреть личную информацию': RegistrationDialogCalle.SHOW}
        ])

    def get_info_request_keyboard(self):
        return self.get_inline_keyboard_markup([{
            'Указать информацию': RegistrationDialogCalle.SELECT_ATTRIBUTE
        }])

    def get_ok_request_keyboard(self):
        return self.get_inline_keyboard_markup([{
            self.OK: RegistrationDialogCalle.END
        }])

    def get_select_attribute_keyboard(self):
        return self.get_inline_keyboard_markup([
            {
                self.FULL_NAME: self.FULL_NAME,
                self.GROUP: self.GROUP,
                self.SUBGROUP: self.SUBGROUP
            },
            {
                'Подтвердить': RegistrationDialogCalle.END
            }
        ])


class RegistrationDialogCalle:
    # states
    (
        ADD_USER,
        SELECT_ACTION,
        DESCRIBE_USER,
        SELECT_ATTRIBUTE,
        SPECIFY_ATTRIBUTE,
        TYPE,
        STOP,
        SHOW
    ) = map(chr, range(1, 9))
    END = ConversationHandler.END

    def __init__(self, ssh: SpreadsheetHandler):
        self._ssh = ssh
        self._udm = UserDataManager()
        self._rkb = RegistrationKeyboardBuilder()

    def start_conversation(self, update: Update, context: CallbackContext) -> str:
        bot_data = context.bot_data
        reg_text = 'Вы зарегистрированы.'
        reg_keyboard = self._rkb.get_primary_keyboard_if_registered()

        if self._udm.is_updated_callback(bot_data) and update.callback_query:
            if self._udm.is_error_occurred(bot_data):
                text = self._udm.get_error(bot_data)
            else:
                text = reg_text
            update.callback_query.answer()
            update.callback_query.edit_message_text(
                text=text, reply_markup=reg_keyboard
            )
        else:
            update.message.reply_text(
                'Привет! Я бот Роман.'
            )
            if self._ssh.get_student_by_username(update.message.from_user.username) == {}:
                text = (
                    'Для начала работы необходимо указать персональную информацию. '
                    'Пожалуйста, зарегистрируйтесь.'
                )
                update.message.reply_text(
                    text=text, reply_markup=self._rkb.get_primary_keyboard_if_not_registered()
                )
            else:
                update.message.reply_text(
                    text=reg_text, reply_markup=reg_keyboard
                )

        self._udm.update_callback(bot_data, False)
        return self.SELECT_ACTION

    def _get_info_request_text(self):
        return f'{self._rkb.OK}, укажите информацию о себе.'

    def add_user(self, update: Update, context: CallbackContext) -> str:
        user_data = context.user_data
        self._udm.set_user_id(user_data, update.effective_user.id)
        self._udm.set_username(user_data, update.effective_user.username)
        user_data[self._udm.get_username(user_data)] = self._udm.get_user_id(user_data)

        text = self._get_info_request_text()
        keyboard = self._rkb.get_info_request_keyboard()

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

        return self.DESCRIBE_USER

    def _get_user_info(self, user_attrs):
        return f"\n{self._rkb.FULL_NAME}: {user_attrs.get(self._rkb.FULL_NAME, '-')}" \
               f"\n{self._rkb.GROUP}: {user_attrs.get(self._rkb.GROUP, '-')}" \
               f"\n{self._rkb.SUBGROUP}: {user_attrs.get(self._rkb.SUBGROUP, '-')}"

    def show_user_info(self, update: Update, context: CallbackContext) -> str:
        user_data = context.user_data

        def get_info() -> str:
            user_attrs = self._udm.get_user_attrs_by_id(user_data)

            if not user_attrs:
                return '\nВы не зарегистрированы.'

            return self._get_user_info(user_attrs)

        text_info = f"{self._rkb.INFO}:\n{get_info()}"

        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=text_info, reply_markup=self._rkb.get_ok_request_keyboard()
        )

        self._udm.update_callback(context.bot_data, True)
        return self.SHOW

    def show_concrete_user_info(self, update: Update, context: CallbackContext) -> str:
        user_data = context.user_data

        def get_info(id_name: str) -> str:
            user_attrs = self._ssh.get_student_by_username(id_name)

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
        bot_data = context.bot_data
        keyboard = self._rkb.get_select_attribute_keyboard()

        if self._udm.is_updated_callback(bot_data):
            if self._udm.is_error_occurred(bot_data):
                text = self._udm.get_error(bot_data)
            else:
                text = 'Отлично! Выберите другой параметр.'
            update.message.reply_text(text=text, reply_markup=keyboard)
        else:
            self._udm.set_user_attrs(user_data, {})
            if self._udm.is_error_occurred(bot_data):
                text = self._udm.get_error(bot_data)
            else:
                text = 'Выберите параметр.'

            update.callback_query.answer()
            update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

        self._udm.update_callback(bot_data, False)
        return self.SPECIFY_ATTRIBUTE

    def request_attribute(self, update: Update, context: CallbackContext) -> str:
        self._udm.set_cur_user_attr_key(context.user_data, update.callback_query.data)
        text = f'{self._rkb.OK}, расскажите.'

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text)

        return self.TYPE

    def save_attribute(self, update: Update, context: CallbackContext) -> str:
        user_data = context.user_data
        bot_data = context.bot_data
        text = update.message.text

        if self._udm.get_cur_user_attr_key(user_data) == self._rkb.FULL_NAME \
                and not EntryChecker.is_name_correct(text):
            self._udm.set_error(bot_data, 'Данные не корректны. Повторите.')
        else:
            self._udm.set_cur_user_attr(user_data, text)

        self._udm.update_callback(bot_data, True)
        return self.select_attribute(update, context)

    def end_describing(self, update: Update, context: CallbackContext) -> int:
        user_data = context.user_data
        bot_data = context.bot_data
        user_attrs = self._udm.get_user_attrs(user_data)
        self._udm.set_user(user_data, user_attrs)

        full_name = user_attrs.get(self._rkb.FULL_NAME)
        group = user_attrs.get(self._rkb.GROUP)
        subgroup = user_attrs.get(self._rkb.SUBGROUP)

        if not full_name or not group or not subgroup:
            self._udm.set_error(bot_data, 'Вы не были зарегистрированы, так как не всё рассказали о себе.')
        else:
            self._ssh.add_student(self._udm.get_username(user_data), full_name, group, subgroup)

        self._udm.update_callback(bot_data, True)
        self.start_conversation(update, context)

        return self.END

    def stop_describing(self, update: Update, context: CallbackContext) -> str:
        update.message.reply_text(f'{self._rkb.OK}, до встречи.')

        return self.STOP
