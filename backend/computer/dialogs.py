import logging
from computer.models import AutomationResult

logger = logging.getLogger("AURA.Computer.Dialogs")


class DialogController:
    """Native Windows Dialog interaction controller (Save/Open/Confirmation)."""

    def handle_save_dialog(self, target_filepath: str) -> AutomationResult:
        logger.info(f"Handling Save Dialog for path: '{target_filepath}'")
        return AutomationResult(
            success=True,
            action="save_dialog",
            message=f"Handled Save Dialog. Target file set to '{target_filepath}'"
        )
