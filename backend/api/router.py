import logging
from typing import Any, Dict
from api.graphql import GraphQLRouter
from api.models import APIResponse
from api.rest import RESTRouter

logger = logging.getLogger("AURA.API.Router")


class UnifiedAPIRouter:
    """Unified API router delegating between REST and GraphQL protocol handlers."""

    def __init__(self):
        self.rest_router = RESTRouter()
        self.graphql_router = GraphQLRouter()

    def route(self, protocol: str, method: str, path: str, body: Dict[str, Any]) -> APIResponse:
        if protocol.lower() == "graphql":
            query = body.get("query", "")
            variables = body.get("variables", {})
            return self.graphql_router.execute_query(query, variables)
        return self.rest_router.handle_request(method, path, body)
