import logging
from typing import Any, Dict
from api.models import APIResponse

logger = logging.getLogger("AURA.API.REST")


class RESTRouter:
    """REST Endpoint Router handling Workflows, Memory, Knowledge, Plugins, and Tools."""

    def handle_request(self, method: str, path: str, body: Dict[str, Any]) -> APIResponse:
        logger.info(f"REST Request [{method}] {path}")

        clean_path = path.lower().strip("/")

        if clean_path.endswith("workflows"):
            return APIResponse(success=True, status_code=200, message="Workflow API", data={"workflows": []})
        elif clean_path.endswith("memory"):
            return APIResponse(success=True, status_code=200, message="Memory API", data={"memories": []})
        elif clean_path.endswith("knowledge"):
            return APIResponse(success=True, status_code=200, message="Knowledge API", data={"knowledge_bases": []})
        elif clean_path.endswith("plugins"):
            return APIResponse(success=True, status_code=200, message="Plugins API", data={"plugins": []})
        elif clean_path.endswith("tools"):
            return APIResponse(success=True, status_code=200, message="Tools API", data={"tools": []})

        return APIResponse(success=False, status_code=404, message=f"Endpoint '{path}' not found.")
