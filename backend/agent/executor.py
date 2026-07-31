class TaskExecutor:

    def execute(self, plan):

        for task in plan.tasks:

            print(
                f"Executing {task.action}"
            )

            task.status = "completed"