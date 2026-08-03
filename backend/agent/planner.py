import json
import logging
import re
from typing import List
from agent.state import TaskStatus, WorkflowState
from agent.task import Task
from agent.workflow import Workflow

logger = logging.getLogger("AURA.Agent.Planner")


class AgentPlanner:
    """
    Planner Engine for decomposing high-level user goals into structured, ordered Workflows.
    """

    def plan_goal(self, goal: str) -> Workflow:
        """
        Decompose a goal into a multi-step Workflow.

        Args:
            goal (str): User goal instruction text.

        Returns:
            Workflow: Constructed workflow containing task graph.
        """
        logger.info(f"Planning workflow for goal: '{goal}'")
        workflow = Workflow(goal=goal, status=WorkflowState.PLANNING)

        # 1. Try LLM Planner
        try:
            tasks = self._plan_with_llm(goal)
            if tasks:
                workflow.tasks = tasks
                workflow.status = WorkflowState.READY
                logger.info(f"Generated LLM workflow plan with {len(tasks)} task(s).")
                return workflow
        except Exception as e:
            logger.debug(f"LLM Planner unavailable ({e}). Using heuristic rule-based planner.")

        # 2. Rule-Based / Heuristic Fallback Planner
        tasks = self._heuristic_plan(goal)
        workflow.tasks = tasks
        workflow.status = WorkflowState.READY
        logger.info(f"Generated heuristic workflow plan with {len(tasks)} task(s).")
        return workflow

    def _plan_with_llm(self, goal: str) -> List[Task]:
        from ai.llm import ask_ai
        prompt = (
            f"You are the Agent Planner for AURA AI Operating System.\n"
            f"Decompose the following user goal into an ordered sequence of executable tool tasks.\n"
            f"Available tools: open_application, calculator, chat, analyze_image, read_screen, read_document, capture_screenshot, camera_capture.\n\n"
            f"Goal: {goal}\n\n"
            f"Return JSON list of tasks:\n"
            f"[{{\"tool_name\": \"open_application\", \"parameters\": {{\"application\": \"chrome\"}}, \"priority\": 1}}]"
        )
        response = ask_ai(prompt)
        parsed = self._parse_json_tasks(response)
        return parsed

    def _parse_json_tasks(self, text: str) -> List[Task]:
        if not text:
            return []
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            items = json.loads(cleaned.strip())
            tasks = []
            prev_id = None
            for idx, item in enumerate(items):
                t = Task(
                    tool_name=item.get("tool_name", "chat"),
                    parameters=item.get("parameters", {}),
                    priority=item.get("priority", idx + 1),
                    dependencies=[prev_id] if prev_id else []
                )
                tasks.append(t)
                prev_id = t.task_id
            return tasks
        except Exception:
            return []

    def _heuristic_plan(self, goal: str) -> List[Task]:
        lower = goal.lower().strip()
        tasks: List[Task] = []

        # Scenario 1: Document PDF & Summarize
        if "pdf" in lower or ("document" in lower and "summarize" in lower):
            t1 = Task(
                tool_name="read_document",
                parameters={"filepath": "document.pdf"},
                priority=1
            )
            t2 = Task(
                tool_name="chat",
                parameters={"message": f"Summarize the document content from task {t1.task_id}"},
                priority=2,
                dependencies=[t1.task_id]
            )
            return [t1, t2]

        # Scenario 2: Screen capture / Vision check
        if any(k in lower for k in ["screenshot", "read screen", "check screen", "look at screen"]):
            t1 = Task(
                tool_name="read_screen",
                parameters={},
                priority=1
            )
            return [t1]

        # Scenario 3: Multiple Apps (e.g. Open Chrome and search OpenAI)
        if "open" in lower:
            apps = [a for a in ["chrome", "notepad", "calculator", "calc"] if a in lower]
            if apps:
                prev_id = None
                for idx, app in enumerate(apps):
                    target = "calculator" if app == "calc" else app
                    t = Task(
                        tool_name="open_application",
                        parameters={"application": target},
                        priority=idx + 1,
                        dependencies=[prev_id] if prev_id else []
                    )
                    tasks.append(t)
                    prev_id = t.task_id
                return tasks

        # Scenario 4: Math / Calculation
        if any(k in lower for k in ["calculate", "+", "-", "*", "/"]):
            expr_match = re.search(r"(\d+\s*[\+\-\*/]\s*\d+)", goal)
            expr = expr_match.group(1) if expr_match else ""
            t1 = Task(
                tool_name="calculator",
                parameters={"expression": expr},
                priority=1
            )
            return [t1]

        # Default Single Task Fallback
        return [Task(tool_name="chat", parameters={"message": goal}, priority=1)]
