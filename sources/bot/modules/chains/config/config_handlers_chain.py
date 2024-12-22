import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Document

from ....loggers import LogInstaller
from ....modules.handlers_chain import HandlersChain
from ....modules.handlers_registrar import HandlersRegistrar as Registrar
from ....modules.keyboard.keyboard import KeyboardBuilder
from ....storage.spreadsheet.util.spreadsheet_config import SpreadsheetConfig
from ....storage.spreadsheet.util.validators import validate_json_filename, validate_and_extract_id


class ConfigKeyboardBuilder:
    @staticmethod
    def get_cancel_keyboard():
        return KeyboardBuilder.get_inline_keyboard_markup(
            [
                {
                    "Вернуться": "cancel_config",
                }
            ]
        )

    @staticmethod
    def get_start_config_keyboard():
        return KeyboardBuilder.get_inline_keyboard_markup(
            [
                {
                    "Люди": "auth_config",
                    "Лаб. работы": "works_config",
                    "Тесты": "tests_config",
                }
            ]
        )

    @staticmethod
    def get_config_keyboard():
        return KeyboardBuilder.get_inline_keyboard_markup(
            [
                {
                    "Ссылка на таблицу": "set_id",
                    "Токен": "set_token",
                }
            ]
        )


class ConfigStates(StatesGroup):
    auth = State()
    waiting_for_auth_id = State()
    waiting_for_auth_token = State()
    work = State()
    waiting_for_works_id = State()
    waiting_for_works_token = State()
    test = State()
    waiting_for_test_id = State()
    waiting_for_test_token = State()


class ConfigHandlersChain(HandlersChain):
    _logger = LogInstaller.get_default_logger(__name__, LogInstaller.DEBUG)

    @staticmethod
    @Registrar.message_handler(commands=["config"])
    async def config_handler(message: types.Message, state: FSMContext):
        data = await state.get_data()
        if data["type"] == "teacher":
            await message.answer(
                "Конфигура",
                reply_markup=ConfigKeyboardBuilder.get_start_config_keyboard(),
            )

    @staticmethod
    @Registrar.callback_query_handler(text="auth_config")
    async def auth_handler(query: types.CallbackQuery, state: FSMContext):
        await ConfigStates.auth.set()
        await ConfigHandlersChain._send_config_keyboard(query.message)

    @staticmethod
    @Registrar.callback_query_handler(text="works_config")
    async def work_handler(query: types.CallbackQuery, state: FSMContext):
        await ConfigStates.auth.set()
        await ConfigHandlersChain._send_config_keyboard(query.message)

    @staticmethod
    @Registrar.callback_query_handler(text="tests_config")
    async def test_handler(query: types.CallbackQuery, state: FSMContext):
        await ConfigStates.auth.set()
        await ConfigHandlersChain._send_config_keyboard(query.message)

    @staticmethod
    async def _send_config_keyboard(message):
        await message.edit_text(
            "Config",
            reply_markup=ConfigKeyboardBuilder.get_config_keyboard(),
        )

    @staticmethod
    @Registrar.callback_query_handler(text="set_id", state=ConfigStates.auth)
    async def set_id_handler(query: types.CallbackQuery, state: FSMContext):
        await ConfigStates.next()
        await query.message.edit_text("Введите ссылку на таблицу:")

    @staticmethod
    @Registrar.message_handler(state=ConfigStates.waiting_for_auth_id)
    async def auth_id_message_handler(message: types.Message, state: FSMContext):
        await ConfigHandlersChain._set_id(message, state, attribute="auth_id")

    @staticmethod
    @Registrar.message_handler(state=ConfigStates.waiting_for_works_id)
    async def work_id_message_handler(message: types.Message, state: FSMContext):
        await ConfigHandlersChain._set_id(message, state, attribute="work_id")

    @staticmethod
    @Registrar.message_handler(state=ConfigStates.waiting_for_test_id)
    async def test_id_message_handler(message: types.Message, state: FSMContext):
        await ConfigHandlersChain._set_id(message, state, attribute="test_id")

    @staticmethod
    async def _set_id(message: types.Message, state: FSMContext, *, attribute):
        spreadsheet_id = validate_and_extract_id(str(message.text))
        if spreadsheet_id:
            SpreadsheetConfig.set_value_and_save(attribute, spreadsheet_id)
            await ConfigHandlersChain._success_id_set(message)
            await state.reset_state()
            username = message.from_user.username
            await state.update_data(username=username)
        else:
            await message.answer(
                "Неправильный ID таблицы, попробуйте еще раз.",
                reply_markup=ConfigKeyboardBuilder.get_cancel_keyboard(),
            )

    @staticmethod
    async def _success_id_set(message):
        await message.answer("Идентификатор таблицы успешно установлен!")

    @staticmethod
    @Registrar.callback_query_handler(text="set_token", state=ConfigStates.auth)
    async def set_token_handler(query: types.CallbackQuery, state: FSMContext):
        await ConfigStates.next()
        await ConfigStates.next()
        await query.message.edit_text("Отправьте .json с токеном:")

    @staticmethod
    @Registrar.message_handler(
        content_types=types.ContentType.DOCUMENT,
        state=ConfigStates.waiting_for_auth_token,
    )
    async def auth_token_message_handler(message: types.Message, state: FSMContext):
        await ConfigHandlersChain._set_token(message, state, attribute="auth_token")

    @staticmethod
    @Registrar.message_handler(
        content_types=types.ContentType.DOCUMENT,
        state=ConfigStates.waiting_for_works_token,
    )
    async def work_token_message_handler(message: types.Message, state: FSMContext):
        await ConfigHandlersChain._set_token(message, state, attribute="work_token")

    @staticmethod
    @Registrar.message_handler(
        content_types=types.ContentType.DOCUMENT,
        state=ConfigStates.waiting_for_test_token,
    )
    async def test_token_message_handler(message: types.Message, state: FSMContext):
        await ConfigHandlersChain._set_token(message, state, attribute="test_token")

    @staticmethod
    async def _set_token(message: types.Message, state: FSMContext, *, attribute):
        document = message.document
        if validate_json_filename(document.file_name):
            file_path = await ConfigHandlersChain._save_file(document)
            SpreadsheetConfig.set_value_and_save(attribute, file_path)
            await ConfigHandlersChain._success_token_set(message)
            await state.reset_state()
        else:
            await message.answer(
                "Пожалуйста, отправьте файл в формате .json. Попробуйте еще раз.",
                reply_markup=ConfigKeyboardBuilder.get_cancel_keyboard(),
            )

    @staticmethod
    async def _save_file(document: Document):
        path = os.path.join(SpreadsheetConfig.json_dir_path, document.file_name)
        await document.download(destination_file=path, make_dirs=True)
        return path

    @staticmethod
    async def _success_token_set(message):
        await message.answer("Токен таблицы успешно установлен!")

    @staticmethod
    @Registrar.callback_query_handler(text="cancel_config", state="*")
    async def cancel_survey_handler(query: types.CallbackQuery, state: FSMContext):
        await query.message.edit_text("Отправка опроса отменена")
        await state.reset_state()
        username = query.message.from_user.username
        await state.update_data(username=username)
