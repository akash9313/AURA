import logging
from workflow.dependency_graph import DependencyGraph
from workflow.workflow import Workflow

logger = logging.getLogger("AURA.Workflow.Validator")


class WorkflowValidator:
    """Validates workflow graph structural completeness and DAG safety."""

    def validate(self, workflow: Workflow) -> bool:
        if not workflow.tasks:
            raise ValueError(f"Workflow '{workflow.workflow_id}' contains no tasks.")

        # Check DAG cycle validity
        dep_graph = DependencyGraph(workflow.tasks)
        dep_graph.validate_dag()
        logger.info(f"Workflow '{workflow.workflow_id}' passed DAG validation successfully.")
        return True
