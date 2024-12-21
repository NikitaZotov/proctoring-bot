from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from ....loggers import LogInstaller
from ...handlers_chain import HandlersChain
from ...handlers_registrar import HandlersRegistrar as Registrar
from ....storage.spreadsheet.subjects.subject_spreadsheet_handler import SubjectSpreadsheetHandler


class SubjectStates(StatesGroup):
    waiting_for_subject_name = State()
    waiting_for_subject_description = State()
    waiting_for_subject_lookup = State()


class SubjectHandlersChain(HandlersChain):
    _logger = LogInstaller.get_default_logger(__name__, LogInstaller.DEBUG)

    @staticmethod
    @Registrar.message_handler(commands=["subject_description_add"], state="*")
    async def subject_start_message_handler(message: types.Message):
        """
        Asks user to add to sheet new subject.
       :param message: User message data
       :type message: :obj:`types.Message`

       :param state: User state machine context
       :type state: :obj:`FSMContext`
        """
        SubjectHandlersChain._logger.debug("Start subject conversation state")
        await message.answer("Введите название дисциплины:")
        await SubjectStates.waiting_for_subject_name.set()

    @staticmethod
    @Registrar.callback_query_handler(text="subject_description_add")
    async def subject_start_callback_handler(query: types.CallbackQuery):
        """
        Asks user to set title of the new subject.
       :param query: User message data
       :type types.CallbackQuery: :obj:`types.Message`

       :param state: User state machine context
       :type state: :obj:`FSMContext`
        """
        SubjectHandlersChain._logger.debug("Start subject conversation state")
        await Registrar.bot.send_message(query.from_user.id, "Введите название дисциплины:")
        await SubjectStates.waiting_for_subject_name.set()


    @staticmethod
    @Registrar.message_handler(state=SubjectStates.waiting_for_subject_name)
    async def subject_name_handler(message: types.Message, state: FSMContext):
        """
        Asks user to set title of the new subject.
       :param message: User message data
       :type message: :obj:`types.Message`

       :param state: User state machine context
       :type state: :obj:`FSMContext`
        """
        subject_name = message.html_text.strip()

        if not subject_name:
            await message.answer("Название дисциплины не может быть пустым. Попробуйте еще раз:")
            return

        await state.update_data(subjects={"subject_title": subject_name})
        await message.answer("Введите описание дисциплины:")
        await SubjectStates.waiting_for_subject_description.set()

    @staticmethod
    @Registrar.message_handler(state=SubjectStates.waiting_for_subject_description)
    async def subject_description_handler(message: types.Message, state: FSMContext):
        """
        Asks user to set description of the new subject.
       :param message: User message data
       :type message: :obj:`types.Message`

       :param state: User state machine context
       :type state: :obj:`FSMContext`
        """
        subject_description = message.html_text.strip()

        if not subject_description:
            await message.answer("Описание дисциплины не может быть пустым. Попробуйте еще раз:")
            return

        data = await state.get_data()
        subject_data = data["subjects"]
        subject_data["subject_text"] = subject_description
        subject_name = data.get('subject_name')
        try:
            await state.update_data(subjects=subject_data)

            await message.answer("Название и описание дисциплины успешно сохранены в таблицу.")
            username = message.from_user.username
            await state.update_data(username=username)
        except Exception as e:
            SubjectHandlersChain._logger.error(f"Error adding subject: {e}")
            await message.answer("Произошла ошибка при сохранении данных. Попробуйте позже.")

        SubjectHandlersChain._logger.debug(
            f"Finite subject conversation state. Name: {subject_name}, Description: {subject_description}"
        )
        await state.finish()

    @staticmethod
    @Registrar.callback_query_handler(text="get_subject_description")
    async def subject_description_lookup_handler(query: types.CallbackQuery):
        """
        Asks user enter the title of subject.
       :param message: User message data
       :type message: :obj:`types.Message`

       :param state: User state machine context
       :type state: :obj:`FSMContext`
        """
        SubjectHandlersChain._logger.debug("Start subject description lookup")
        await Registrar.bot.send_message(query.from_user.id, "Введите название дисциплины:")
        await SubjectStates.waiting_for_subject_lookup.set()

    @staticmethod
    @Registrar.message_handler(state=SubjectStates.waiting_for_subject_lookup)
    async def subject_lookup_handler(message: types.Message, state: FSMContext):
        """
        Asks user enter the title of subject.
       :param message: User message data
       :type message: :obj:`types.Message`

       :param state: User state machine context
       :type state: :obj:`FSMContext`
        """
        subject_name = message.text.strip()
        if not subject_name:
            await message.answer("Название дисциплины не может быть пустым. Попробуйте ещё раз.")
            return

        try:
            data = await state.get_data()
            subjects = data.get("subjects")

            for subject in subjects:
                if subject["subject_title"] == subject_name:
                    description = subject["subject_text"]

            await message.answer(f"Информация о дисциплине \"{subject_name}\":\n{description}",
                                 parse_mode="HTML")
        except Exception as e:
            SubjectHandlersChain._logger.error(f"Error fetching description: {e}")
            await message.answer(f"Не удалось найти описание для дисциплины '{subject_name}'."
                                 f" Проверьте название и попробуйте снова.")
        finally:
            await state.finish()