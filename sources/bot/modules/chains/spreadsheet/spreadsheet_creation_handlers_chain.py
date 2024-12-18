from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from sources.bot.loggers import LogInstaller
from ...handlers_registrar import HandlersRegistrar as Registrar


# States for the spreadsheet creation process
class SpreadsheetStates(StatesGroup):
    waiting_for_spreadsheet_name = State()
    waiting_for_column_names = State()
    waiting_for_table_mode = State()


# Handlers for spreadsheet-related operations
class SpreadsheetHandlersChain:
    _logger = LogInstaller.get_default_logger(__name__, LogInstaller.DEBUG)

    @staticmethod
    @Registrar.message_handler(commands=["create_table"], state="*")
    async def start_table_creation(message: types.Message, state: FSMContext):
        """Initiates the table creation process."""
        data = await state.get_data()
        if data.get("type") == "teacher":
            cancel_button = InlineKeyboardMarkup().add(
                InlineKeyboardButton("Отмена", callback_data="cancel_table")
            )
            await message.answer("Введите название таблицы:", reply_markup=cancel_button)
            await SpreadsheetStates.waiting_for_spreadsheet_name.set()

    @staticmethod
    @Registrar.message_handler(state=SpreadsheetStates.waiting_for_spreadsheet_name)
    async def receive_spreadsheet_name(message: types.Message, state: FSMContext):
        """Handles the input for spreadsheet name."""
        spreadsheet_name = message.text.strip()
        if not spreadsheet_name:
            await message.answer("Ошибка: название таблицы не может быть пустым. Попробуйте снова.")
            return

        await state.update_data(spreadsheet_name=spreadsheet_name)
        cancel_button = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Отмена", callback_data="cancel_table")
        )
        await message.answer("Введите названия столбцов через \"|\" (например: столбец1|столбец2|столбец3):", reply_markup=cancel_button)
        await SpreadsheetStates.waiting_for_column_names.set()

    @staticmethod
    @Registrar.message_handler(state=SpreadsheetStates.waiting_for_column_names)
    async def receive_column_names(message: types.Message, state: FSMContext):
        """Handles the input for column names."""
        column_names = [name.strip() for name in message.text.split("|")]
        if len(column_names) == 0:
            await message.answer("Ошибка: введите хотя бы одно название столбца.")
            return

        await state.update_data(column_names=column_names)

        # Кнопки для выбора режима
        mode_buttons = InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("Редактирование", callback_data="set_mode_writer"),
            InlineKeyboardButton("Только для чтения", callback_data="set_mode_reader")
        )
        await message.answer("Выберите режим таблицы:", reply_markup=mode_buttons)
        await SpreadsheetStates.waiting_for_table_mode.set()

    @staticmethod
    @Registrar.callback_query_handler(state=SpreadsheetStates.waiting_for_table_mode)
    async def set_table_mode(query: types.CallbackQuery, state: FSMContext):
        """Handles the selection of table mode."""
        mode = "writer" if query.data == "set_mode_writer" else "reader"

        user_data = await state.get_data()
        spreadsheet_name = user_data.get("spreadsheet_name")
        column_names = user_data.get("column_names")

        try:
            # Создание таблицы
            spreadsheet_id = await state.create_spreadsheet(spreadsheet_name, {"list1": [column_names]}, mode)
            await query.message.edit_text(
                f"Таблица '{spreadsheet_name}' успешно создана в режиме '{'редактирования' if mode == 'writer' else 'только для чтения'}'!"
                f"\nСсылка: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid=0"
                f"\nId:\n{spreadsheet_id}"
            )
        except Exception as e:
            await query.message.edit_text(f"Произошла ошибка при создании таблицы: {e}")

        await state.finish()

    @staticmethod
    @Registrar.callback_query_handler(text="cancel_table", state="*")
    async def cancel_table_creation(query: types.CallbackQuery, state: FSMContext):
        """Handles cancellation of the table creation process."""
        await query.message.edit_text("Создание таблицы отменено.")
        await state.reset_state()
