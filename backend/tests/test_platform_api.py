import unittest
from api.auth import APIAuthenticator
from api.gateway import APIGateway
from api.models import APIScope
from api.permissions import ScopePermissionValidator
from api.rate_limit import APIRateLimiter
from api.sdk.python.aura_platform_sdk import AuraPlatformClient
from api.telemetry import APITelemetryRecorder
from api.versioning import APIVersionManager


class TestPlatformAPI(unittest.TestCase):

    def test_api_authenticator(self):
        """Test API Key creation and verification."""
        auth = APIAuthenticator()
        key = auth.create_api_key("DevKey", [APIScope.READ_MEMORY, APIScope.EXECUTE_WORKFLOW])
        self.assertIsNotNone(key.key_id)

        verified = auth.verify_key(key.secret_key)
        self.assertEqual(verified.key_id, key.key_id)

    def test_scope_permission_validator(self):
        """Test scope permission checks."""
        auth = APIAuthenticator()
        key = auth.create_api_key("WorkflowKey", [APIScope.EXECUTE_WORKFLOW])
        val = ScopePermissionValidator()

        self.assertTrue(val.check_scope(key, APIScope.EXECUTE_WORKFLOW))
        self.assertFalse(val.check_scope(key, APIScope.WRITE_MEMORY))

    def test_rate_limiter(self):
        """Test APIRateLimiter limits requests per minute."""
        limiter = APIRateLimiter()
        key_id = "test_key_1"
        for _ in range(60):
            self.assertTrue(limiter.is_allowed(key_id))
        self.assertFalse(limiter.is_allowed(key_id))

    def test_version_manager(self):
        """Test API versioning fallback."""
        vm = APIVersionManager()
        self.assertEqual(vm.validate_version("v1"), "v1")
        self.assertEqual(vm.validate_version("v99"), "v1")

    def test_api_gateway_end_to_end(self):
        """Test APIGateway middleware pipeline and endpoint routing."""
        gateway = APIGateway()
        key = gateway.authenticator.create_api_key("MasterKey", [APIScope.READ_MEMORY])

        # 1. Valid request
        res = gateway.handle_api_request(
            secret_key=key.secret_key,
            method="GET",
            path="/api/v1/memory",
            required_scope=APIScope.READ_MEMORY
        )
        self.assertTrue(res.success)
        self.assertEqual(res.status_code, 200)

        # 2. Scope denied request
        res_denied = gateway.handle_api_request(
            secret_key=key.secret_key,
            method="POST",
            path="/api/v1/workflows",
            required_scope=APIScope.EXECUTE_WORKFLOW
        )
        self.assertFalse(res_denied.success)
        self.assertEqual(res_denied.status_code, 403)

    def test_python_sdk_client(self):
        """Test official Python SDK client wrapper."""
        client = AuraPlatformClient(api_key="sk_test")
        res = client.get_workflows()
        self.assertTrue(res["success"])


if __name__ == "__main__":
    unittest.main()
