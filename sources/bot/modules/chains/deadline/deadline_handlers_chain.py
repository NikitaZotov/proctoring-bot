from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import (
    StatesGroup,
    State,
)

from ....loggers import LogInstaller
from ...handlers_chain import HandlersChain
from ...handlers_registrar import HandlersRegistrar as Registrar
from ....storage.spreadsheet.deadline.deadline_spreadsheet_handler import DeadlineSpreadsheetHandler


class DeadlineStates(StatesGroup):
    waiting_for_link = State()


class DeadlineHandlersChain(HandlersChain):
    _logger = LogInstaller.get_default_logger(__name__, LogInstaller.DEBUG)

    @staticmethod
    @Registrar.message_handler(commands=["deadline"], state="*")
    async def deadline_start_handler(message: types.Message, state: FSMContext):
        DeadlineHandlersChain._logger.debug(f"Start deadline conversation state")
        deadlines = await DeadlineHandlersChain._get_user_deadlines()

        if deadlines:
            deadline_message = DeadlineHandlersChain._format_deadlines(deadlines)
            await message.answer(deadline_message)
        else:
            await message.answer("На данный момент нет активных дедлайнов.")

        await state.finish()

    @staticmethod
    @Registrar.callback_query_handler(text="deadline")
    async def deadline_start_handler(query: types.CallbackQuery, state: FSMContext):
        DeadlineHandlersChain._logger.debug(f"Start deadline conversation state")

        deadlines = await DeadlineHandlersChain._get_user_deadlines()
        if deadlines:

            deadline_message = DeadlineHandlersChain._format_deadlines(deadlines)
            await Registrar.bot.send_message(query.from_user.id, deadline_message)
        else:
            await Registrar.bot.send_message(query.from_user.id, "На данный момент нет активных дедлайнов.")

        await state.finish()

    @staticmethod
    async def _get_user_deadlines():
        try:
            deadline_handler = DeadlineSpreadsheetHandler(
                spreadsheet_id='1R8PFRfrb8NRjyCQMZLExXvNEoA8_xvDTACvmdExO70U',
                file_name='./sources/tokens/works_token.json'
            )

            deadlines = deadline_handler.get_deadlines()

            formatted_deadlines = [
                {
                    "discipline": deadline.get("discipline_name"),
                    "lab_name": deadline.get("lab_name"),
                    "deadline": deadline.get("deadline"),
                    "description": deadline.get("description", "")
                }
                for deadline in deadlines
            ]

            return formatted_deadlines

        except Exception as e:
            DeadlineHandlersChain._logger.error(f"Error getting deadlines: {e}")
            return []

    @staticmethod
    def _format_deadlines(deadlines):
        message = "Ваши текущие дедлайны:\n\n"

        for deadline in deadlines:
            message += (
                f"Дисциплина: {deadline['discipline']}\n"
                f"Лабораторная: {deadline['lab_name']}\n"
                f"Дедлайн: {deadline['deadline']}\n"
                f"Описание: {deadline['description']}\n\n"
            )

        return message

    @staticmethod
    @Registrar.callback_query_handler(text="deadline_subject")
    async def deadline_by_subject_handler(query: types.CallbackQuery, state: FSMContext):
        DeadlineHandlersChain._logger.debug(f"User @{query.from_user.username} requested deadlines by subject.")
        await DeadlineStates.waiting_for_link.set()
        await state.update_data(last_callback="deadline_subject")
        await query.message.answer("Введите название дисциплины:")

    @staticmethod
    @Registrar.message_handler(state=DeadlineStates.waiting_for_link)
    async def deadline_subject_input_handler(message: types.Message, state: FSMContext):
        discipline_name = message.text.strip()
        DeadlineHandlersChain._logger.debug(f"User @{message.from_user.username} entered discipline: {discipline_name}")

        spreadsheet_handler = DeadlineSpreadsheetHandler(
            spreadsheet_id='1R8PFRfrb8NRjyCQMZLExXvNEoA8_xvDTACvmdExO70U',
            file_name='./sources/tokens/works_token.json'
        )

        deadlines = spreadsheet_handler.get_deadline(discipline_name=discipline_name)

        if deadlines:
            message_text = "Дедлайны по дисциплине:\n\n"
            for deadline in deadlines:
                message_text += (
                    f"Дисциплина: {deadline['discipline_name']}\n"
                    f"Лабораторная: {deadline['lab_name']}\n"
                    f"Дедлайн: {deadline['deadline']}\n"
                    f"Описание: {deadline['description']}\n\n"
                )
            await message.answer(message_text)
        else:
            await message.answer(f"Дедлайны для дисциплины '{discipline_name}' не найдены.")

        await state.finish()