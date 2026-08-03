import logging
from typing import Any, Dict
from workflow.workflow import Workflow

logger = logging.getLogger("AURA.Workflow.Reporter")


class WorkflowReporter:
    """Generates execution summaries, timelines, and metric reports."""

    def generate_report(self, workflow: Workflow) -> Dict[str, Any]:
        report = {
            "workflow_id": workflow.workflow_id,
            "goal": workflow.goal,
            "status": workflow.state.value,
            "metrics": workflow.metrics.to_dict(),
            "completed_tasks": [
                {"task_id": t.task_id, "tool": t.tool, "description": t.description, "result": t.result}
                for t in workflow.tasks.values() if t.state.value == "completed"
            ],
            "failed_tasks": [
                {"task_id": t.task_id, "tool": t.tool, "description": t.description, "error": t.metrics.error_message}
                for t in workflow.tasks.values() if t.state.value == "failed"
            ]
        }
        logger.info(f"Generated report for workflow '{workflow.workflow_id}' ({workflow.state.value})")
        return report
