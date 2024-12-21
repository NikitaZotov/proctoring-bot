"""
Bot main handlers chain implementation module.
"""
import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ChatType
from aiogram.types import InlineKeyboardMarkup

from ....loggers import LogInstaller
from ...handlers_chain import HandlersChain
from ...handlers_registrar import HandlersRegistrar as Registrar
from ...keyboard.keyboard import KeyboardBuilder
from ..auth.auth_expectation_chain import AuthExpectationHandlersChain
from ....storage.spreadsheet.auth.auth_spreadsheet_handler import AuthSpreadsheetHandler
from ....storage.spreadsheet.works.works_spreadsheet_handler import WorksSpreadsheetHandler


class MainStates(StatesGroup):
    """
    Bot main handlers chain states class implementation.
    """
    SELECT_GROUP = State()
    CHANGE_NAME_USERNAME = State()
    CHANGE_NAME_NEW_NAME = State()
    SET_ADMISSIONS_THRESHOLD = State()
    


class MainKeyboardsBuilder:
    """
    Bot main handlers chain keyboard builder class implementation.
    """

    @staticmethod
    def get_private_start_keyboard() -> InlineKeyboardMarkup:
        """
        Gets keyboard to send message to private user chat.

        :return: Returns inline keyboard markup.
        :rtype: :obj:`InlineKeyboardMarkup`
        """
        return KeyboardBuilder.get_inline_keyboard_markup(
            [
                {
                    "Пройти регистрацию": "auth",
                },
            ]
        )

    @staticmethod
    def get_info_keyboard() -> InlineKeyboardMarkup:
        """
        Gets keyboard to send information about user message to chat.

        :return: Returns inline keyboard markup.
        :rtype: :obj:`InlineKeyboardMarkup`
        """
        return KeyboardBuilder.get_inline_keyboard_markup(
            [
                {
                    "Посмотреть информацию": "info",
                },
                {
                    "Отправить лабораторную работу": "lab",
                },
                {
                    "Редактировать ФИО студента": "change_name",
                },
                {
                    "Выставить допуски": "set_admissions",
                },
            ]
        )


class MainHandlersChain(HandlersChain):
    """
    Bot main handlers chain class implementation.
    """

    _logger = LogInstaller.get_default_logger(__name__, LogInstaller.DEBUG)
    my_spreadsheet_id = "1y82TxM8AuBrVXsDSif8LobwZ1wjIkWDutmoSrIr03b0"
    work_spreadsheet_id = "1fY8Vox86g6zZgYm3Lmpy-7JSNDLAQvEUE7bdYgvR1Zg"
    path_to_token = "../../../../tokens/auth_token.json"
    path_to_work_token = "../../../../tokens/works_token.json"

    @staticmethod
    async def _start_routine(message: types.Message, state: FSMContext):
        username = message.from_user.username
        greeting = f"Привет, {message.from_user.first_name} (@{username}).\n"
        bot = await Registrar.bot.get_me()

        await state.update_data(username=username)
        data = await state.get_data()
        data_size = len(data.get("auth").keys())
        not_registered = data_size != 3 and data_size != 1

        if not_registered:
            MainHandlersChain._logger.debug(f"User @{username} is not registered")
            text = f"{greeting}Вы не зарегистрированы.\nПройти регистрацию: @{bot.username}."
            keyboard_markup = MainKeyboardsBuilder.get_private_start_keyboard()
        else:
            MainHandlersChain._logger.debug(f"User @{username} is registered")
            text = f"{greeting}Вы уже зарегистрированы.\nПодробности: @{bot.username}."
            keyboard_markup = MainKeyboardsBuilder.get_info_keyboard()

        return text, keyboard_markup, not_registered

    @staticmethod
    @Registrar.message_handler(content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
    async def start_handler(message: types.Message, state: FSMContext):
        """
        Asks user ro start registration process or speaks about that he is registered.

        :param message: User message data
        :type message: :obj:`types.Message`

        :param state: User state machine context
        :type state: :obj:`FSMContext`
        """
        MainHandlersChain._logger.debug("Start main group conversation state")
        text, _, not_registered = await MainHandlersChain._start_routine(message, state)

        await Registrar.bot.send_message(chat_id=message.chat.id, text=text)
        await AuthExpectationHandlersChain().wait_registration(message, state, not_registered)

    @staticmethod
    @Registrar.message_handler(commands=["start"], chat_type=ChatType.PRIVATE)
    async def start_handler(message: types.Message, state: FSMContext):
        """
        Starts dialog with user by 'start' command. Shows to user main keyboard to choose action.
        Send to user registration state message.

        :param message: User message data
        :type message: :obj:`types.Message`

        :param state: User state machine context
        :type state: :obj:`FSMContext`
        """
        MainHandlersChain._logger.debug("Start main private conversation state")
        text, keyboard_markup, _ = await MainHandlersChain._start_routine(message, state)
        text = text.replace(f"(@{message.from_user.username})", "")
        await message.answer(text, reply_markup=keyboard_markup)

    @staticmethod
    @Registrar.message_handler(commands=["cancel"], state="*")
    async def cancel_handler(message: types.Message, state: FSMContext):
        """
        Cancels conversation by 'cancel' command.

        Note: Handler may be started everywhere.

        :param message: User message data
        :type message: :obj:`types.Message`

        :param state: User state machine context
        :type state: :obj:`FSMContext`
        """
        current_state = await state.get_state()
        if current_state is None:
            return

        MainHandlersChain._logger.debug(f"Cancel {current_state} conversation state")

        await state.finish()
        await message.answer("Действие отменено")

    @staticmethod
    @Registrar.message_handler(commands=["info"])
    async def get_info_handler(message: types.Message, state: FSMContext):
        """
        Sends to user information: username, name, group and subgroup by 'info' command.

        :param message: User message data
        :type message: :obj:`types.Message`

        :param state: User state machine context
        :type state: :obj:`FSMContext`
        """
        data = await state.get_data()
        await message.answer(MainHandlersChain.get_info(data))

    @staticmethod
    @Registrar.callback_query_handler(text="info")
    async def get_info_handler(query: types.CallbackQuery, state: FSMContext):
        """
        Sends to user information: username, name, group and subgroup by 'info' callback query message.

        :param query: Callback query message
        :type query: :obj:`types.CallbackQuery`

        :param state: User state machine context
        :type state: :obj:`FSMContext`
        """
        data = await state.get_data()
        await query.message.answer(MainHandlersChain.get_info(data))



    @staticmethod
    def get_info(user_data) -> str:
        """
        Gets to user information: username, name, group and subgroup from spreadsheet storage.

        :param user_data: User data
        :type user_data: :obj:`dict[Any]`

        :return: Returns information about user.
        :rtype: :obj:`str`
        """
        auth_data = user_data.get("auth")

        if user_data["type"] == "student":
            name = auth_data.get("name")
            group = auth_data.get("group")
            subgroup = auth_data.get("subgroup")

            return f"Информация о Вас:\nФИО: {name}\nГруппа: {group}\nПодгруппа: {subgroup}\n"
        elif user_data["type"] == "teacher":
            name = auth_data.get("ФИО")

            return f"Информация о Вас:\nФИО: {name}\n"

    @staticmethod
    @Registrar.message_handler(commands=["change_name"], state="*")
    async def change_name_start(message: types.Message, state: FSMContext):
        """
        Initiates the process of moderating a student's name by showing a list of all students.

        :param message: User message data
        :type message: :obj:`types.Message`

        :param state: User state machine context
        :type state: :obj:`FSMContext`
        """
        try:
            user_data = await state.get_data()

            if user_data.get("type") != "teacher":
                await message.answer("Эта операция доступна только преподавателям.")
                return
            spreadsheet_handler = AuthSpreadsheetHandler(
                spreadsheet_id=MainHandlersChain.my_spreadsheet_id,
                file_name=MainHandlersChain.path_to_token
            )

            usernames = spreadsheet_handler.get_student_usernames()
            if not usernames:
                await message.answer("В таблице нет студентов.")
                return

            students_list = []
            for username_row in usernames:
                username = username_row[0]
                student_info = spreadsheet_handler.get_student_by_username(username)
                fio = student_info.get("name", "Не указано")
                students_list.append(f"{username} - {fio}")

            students_text = "\n".join(students_list)
            await message.answer(f"Список всех студентов:\n{students_text}")

            await message.answer("Введите ник студента, имя которого нужно изменить:")
            await state.set_state(MainStates.CHANGE_NAME_USERNAME)

        except Exception as e:
            MainHandlersChain._logger.error(f"Failed to fetch student list: {e}")
            await message.answer("Произошла ошибка при получении списка студентов. Попробуйте позже.")
            await state.finish()


    @staticmethod
    @Registrar.callback_query_handler(text="change_name")
    async def change_name_start_callback(query: types.CallbackQuery, state: FSMContext):
        """
        Initiates the process of moderating a student's name by showing a list of all students.
        Called when the user presses the "Редактировать ФИО студента" button.
        """
        try:
            user_data = await state.get_data()

            if user_data.get("type") != "teacher":
                await query.message.answer("Эта операция доступна только преподавателям.")
                return
            spreadsheet_handler = AuthSpreadsheetHandler(
                spreadsheet_id=MainHandlersChain.my_spreadsheet_id,
                file_name=MainHandlersChain.path_to_token
            )

            usernames = spreadsheet_handler.get_student_usernames()
            if not usernames:
                await query.message.answer("В таблице нет студентов.")
                return

            students_list = []
            for username_row in usernames:
                username = username_row[0]
                student_info = spreadsheet_handler.get_student_by_username(username)
                fio = student_info.get("name", "Не указано")
                students_list.append(f"{username} - {fio}")

            students_text = "\n".join(students_list)
            await query.message.answer(f"Список всех студентов:\n{students_text}")

            await query.message.answer("Введите ник студента, имя которого нужно изменить:")
            await state.set_state(MainStates.CHANGE_NAME_USERNAME)

        except Exception as e:
            MainHandlersChain._logger.error(f"Failed to fetch student list: {e}")
            await query.message.answer("Произошла ошибка при получении списка студентов. Попробуйте позже.")
            await state.finish()

    @staticmethod
    @Registrar.message_handler(state=MainStates.CHANGE_NAME_USERNAME)
    async def change_name_get_username(message: types.Message, state: FSMContext):
        """
        Receives the student's username and asks for the new name.

        :param message: User message data
        :type message: :obj:`types.Message`

        :param state: User state machine context
        :type state: :obj:`FSMContext`
        """
        username = message.text.strip()
        await state.update_data(username_to_change=username)
        await message.answer(f"Студент с ником @{username} найден. Введите новое ФИО для студента:")
        await state.set_state(MainStates.CHANGE_NAME_NEW_NAME)

    @staticmethod
    @Registrar.message_handler(state=MainStates.CHANGE_NAME_NEW_NAME)
    async def change_name_set_new_name(message: types.Message, state: FSMContext):
        """
        Receives the new name and updates the student's information.

        :param message: User message data
        :type message: :obj:`types.Message`

        :param state: User state machine context
        :type state: :obj:`FSMContext`
        """
        new_name = message.text.strip()
        data = await state.get_data()
        username_to_change = data.get("username_to_change")

        try:
            spreadsheet_handler = AuthSpreadsheetHandler(spreadsheet_id=MainHandlersChain.my_spreadsheet_id, file_name=MainHandlersChain.path_to_token)
            success = spreadsheet_handler.update_student_name(username=username_to_change, new_name=new_name)

            if success:
                await message.answer(f"ФИО студента с ником @{username_to_change} успешно изменено на '{new_name}'.")
            else:
                await message.answer(f"Не удалось обновить ФИО студента с ником @{username_to_change}.")
        except Exception as e:
            MainHandlersChain._logger.error(f"Failed to update student's name: {e}")
            await message.answer("Произошла ошибка при обновлении имени студента. Попробуйте позже.")

        await state.finish()

    @staticmethod
    @Registrar.message_handler(commands=["set_admissions"], state="*")
    async def set_admissions(message: types.Message, state: FSMContext):
        """
        Sets admissions for students based on the number of lab works.

        :param message: User message data
        :type message: :obj:`types.Message`
        """
        user_data = await state.get_data()

        if user_data.get("type") != "teacher":
            await message.answer("Эта операция доступна только преподавателям.")
            return
        await message.answer("Введите минимальное количество лабораторных для допуска:")
        await state.set_state(MainStates.SET_ADMISSIONS_THRESHOLD)
        
        
    @staticmethod
    @Registrar.callback_query_handler(text="set_admissions")
    async def set_admissions(query: types.CallbackQuery, state: FSMContext):
        """
        Initiates the process of set admissions to students.
        Called when the user presses the "Выставить допуски" button.
        """
        user_data = await state.get_data()

        if user_data.get("type") != "teacher":
            await query.message.answer("Эта операция доступна только преподавателям.")
            return
        await query.message.answer("Введите минимальное количество лабораторных для допуска:")
        await state.set_state(MainStates.SET_ADMISSIONS_THRESHOLD)


    @staticmethod
    @Registrar.message_handler(state=MainStates.SET_ADMISSIONS_THRESHOLD)
    async def process_admissions_threshold(message: types.Message, state: FSMContext):
        """
        Processes the admissions threshold and calculates admissions for all students.

        :param message: User message data
        :type message: :obj:`types.Message`

        :param state: User state machine context
        :type state: :obj:`FSMContext`
        """
        try:
            threshold = int(message.text.strip())

            auth_spreadsheet_handler = AuthSpreadsheetHandler(
                spreadsheet_id=MainHandlersChain.my_spreadsheet_id,
                file_name=MainHandlersChain.path_to_token,
            )
            works_spreadsheet_handler = WorksSpreadsheetHandler(
                spreadsheet_id=MainHandlersChain.work_spreadsheet_id,
                file_name=MainHandlersChain.path_to_work_token,
            )

            students = auth_spreadsheet_handler.get_student_usernames()
            lab_counts = works_spreadsheet_handler.get_student_lab_count()

            admissions = {}
            new_admissions = {}
            for student_row in students:
                username = student_row[0] 
                student_name = auth_spreadsheet_handler.get_student_by_username(username).get("name", "Не указано")
                student_group = auth_spreadsheet_handler.get_student_by_username(username).get("group", "Не указано")
                lab_count = lab_counts.get(username, 0) 

                status = "Допуск" if lab_count >= threshold else "Недопуск"
                admissions[username] = status
                if status == "Допуск":
                    if student_group not in new_admissions:
                        new_admissions[student_group] = [] 
                    new_admissions[student_group].append(student_name)

            auth_spreadsheet_handler.batch_update_admission_status(admissions)

            result_text = "Допущенные студенты:\n"
            for group, students_in_group in new_admissions.items():
                result_text += f"\nГруппа {group}:\n"
                result_text += "\n".join(students_in_group) 
                result_text += "\n" 

            if result_text == "Допущенные студенты:\n":
                await message.answer("Студенты, выполнившие все требования для допуска, отсутствуют.")
            else:
                await message.answer(result_text)
        except ValueError:
            await message.answer("Пожалуйста, введите число.")
        except Exception as e:
            MainHandlersChain._logger.error(f"Failed to process admissions: {e}")
            await message.answer("Произошла ошибка. Попробуйте позже.")
        finally:
            await state.finish()


