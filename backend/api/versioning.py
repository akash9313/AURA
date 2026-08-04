import logging

logger = logging.getLogger("AURA.API.Versioning")


class APIVersionManager:
    """Manages API version compatibility and routing (v1, v2)."""

    SUPPORTED_VERSIONS = ["v1", "v2"]
    DEFAULT_VERSION = "v1"

    def validate_version(self, version_str: str) -> str:
        version_clean = version_str.lower().strip()
        if version_clean in self.SUPPORTED_VERSIONS:
            return version_clean
        logger.warning(f"Unsupported API version '{version_str}', defaulting to '{self.DEFAULT_VERSION}'")
        return self.DEFAULT_VERSION
