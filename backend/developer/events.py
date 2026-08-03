from enum import Enum


class DeveloperEvent(Enum):
    """Event definitions for Developer Mode Engine."""
    PROJECT_OPENED = "project_opened"
    TERMINAL_COMMAND_STARTED = "terminal_command_started"
    TERMINAL_COMMAND_FINISHED = "terminal_command_finished"
    TEST_RUN_COMPLETED = "test_run_completed"
    BUILD_STARTED = "build_started"
    BUILD_COMPLETED = "build_completed"
    GIT_OPERATION_COMPLETED = "git_operation_completed"
    CODE_ANALYSIS_COMPLETED = "code_analysis_completed"
