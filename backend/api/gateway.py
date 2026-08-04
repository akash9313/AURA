import logging
import time
from typing import Any, Dict, Optional
from api.auth import APIAuthenticator
from api.models import APIResponse, APIScope
from api.permissions import ScopePermissionValidator
from api.rate_limit import APIRateLimiter
from api.router import UnifiedAPIRouter
from api.telemetry import APITelemetryRecorder
from api.versioning import APIVersionManager
from api.websocket import WebSocketHandler

logger = logging.getLogger("AURA.API.Gateway")


class APIGateway:
    """
    Master AURA Platform API Gateway Orchestrator.
    Middleware stack: RateLimiter -> Auth -> ScopeValidator -> Versioning -> Router -> Telemetry.
    """

    def __init__(self, bus=None):
        self.bus = bus
        self.authenticator = APIAuthenticator()
        self.permission_validator = ScopePermissionValidator()
        self.rate_limiter = APIRateLimiter()
        self.version_manager = APIVersionManager()
        self.router = UnifiedAPIRouter()
        self.telemetry = APITelemetryRecorder()
        self.websocket = WebSocketHandler()

    def handle_api_request(
        self,
        secret_key: str,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        required_scope: Optional[APIScope] = None,
        version: str = "v1",
        protocol: str = "rest"
    ) -> APIResponse:
        t0 = time.time()
        body = body or {}

        # 1. Authenticate API Key
        api_key = self.authenticator.verify_key(secret_key)
        if not api_key:
            res = APIResponse(success=False, status_code=401, message="Unauthorized: Invalid API secret key.")
            self.telemetry.record_request(path, 401, (time.time() - t0) * 1000.0)
            return res

        # 2. Rate Limiting
        if not self.rate_limiter.is_allowed(api_key.key_id):
            res = APIResponse(success=False, status_code=429, message="Too Many Requests: Rate limit exceeded.")
            self.telemetry.record_request(path, 429, (time.time() - t0) * 1000.0)
            return res

        # 3. Scope Permissions
        if required_scope:
            if not self.permission_validator.check_scope(api_key, required_scope):
                res = APIResponse(success=False, status_code=403, message=f"Forbidden: Key lacks scope '{required_scope.value}'.")
                self.telemetry.record_request(path, 403, (time.time() - t0) * 1000.0)
                return res

        # 4. Versioning
        validated_version = self.version_manager.validate_version(version)

        # 5. Route Request
        res = self.router.route(protocol, method, path, body)
        res.version = validated_version

        dt = (time.time() - t0) * 1000.0
        self.telemetry.record_request(path, res.status_code, dt)
        return res
