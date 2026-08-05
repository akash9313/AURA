"""
Result Formatter.
Formats MissionExecutionResult objects into structured summaries for system reporting and Conversation Manager.
"""

import logging
from typing import Optional

from workflow.integration.models import MissionExecutionResult, MissionExecutionStatus

logger = logging.getLogger("AURA.Workflow.Integration.ResultFormatter")


class ResultFormatter:
    """
    Formats workflow execution results into clean text summaries.
    """

    def format_summary(self, result: MissionExecutionResult) -> str:
        """
        Format MissionExecutionResult into summary string.

        Args:
            result: MissionExecutionResult to format.

        Returns:
            Human-readable summary text.
        """
        if result.status == MissionExecutionStatus.COMPLETED:
            return (
                f"Successfully completed mission '{result.mission_id}' in {result.execution_time_sec:.2f}s. "
                f"Completed {len(result.completed_tasks)} tasks with empirical verification confirmed."
            )
        elif result.status == MissionExecutionStatus.CANCELLED:
            return f"Mission '{result.mission_id}' execution was cancelled before completion."
        elif result.status == MissionExecutionStatus.VERIFICATION_FAILED:
            return f"Mission '{result.mission_id}' failed empirical goal verification."
        else:
            failed_str = ", ".join(result.failed_tasks) if result.failed_tasks else "unknown errors"
            return f"Mission '{result.mission_id}' failed during execution: {failed_str}."
