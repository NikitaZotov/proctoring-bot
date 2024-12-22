"""
Standard bot handlers factory implementation module.
"""

from ...loggers import LogInstaller
from ...modules.chains.auth.auth_handlers_chain import AuthHandlersChain
from ...modules.handlers_registrar import HandlersRegistrar
from ...modules.chains.main.main_handlers_chain import MainHandlersChain
from ...modules.chains.work.work_handlers_chain import WorkHandlersChain
from ...modules.chains.survey.student_handlers_chain import StudentHandlersChain
from ...modules.chains.survey.teacher_handlers_chain import SurveyTeacherHandlersChain
from ...modules.chains.deadline.deadline_handlers_chain import DeadlineHandlersChain
from ...modules.chains.config.config_handlers_chain import ConfigHandlersChain
from ...state_machine import StateMachine
from ...modules.factory.handlers_factory import HandlersFactory


class StandardHandlersFactory(HandlersFactory):
    """
    Standard bot handlers factory class implementation.
    """

    _logger = LogInstaller.get_default_logger(__name__, LogInstaller.ERROR)

    def setup_handlers(self, machine: StateMachine):
        try:
            HandlersRegistrar(machine).register(
                [
                    AuthHandlersChain,
                    MainHandlersChain,
                    WorkHandlersChain,
                    StudentHandlersChain,
                    SurveyTeacherHandlersChain,
                    DeadlineHandlersChain,
                    ConfigHandlersChain,
                ]
            )
        except TypeError as error:
            self._logger.error(error)
