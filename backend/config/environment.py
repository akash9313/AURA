import os
import logging
from typing import Dict, Any

logger = logging.getLogger("AURA.Config.Environment")


class EnvironmentConfigLoader:
    """Environment Variable Configuration Loader."""

    def load_environment_overrides(self) -> Dict[str, Dict[str, Any]]:
        overrides: Dict[str, Dict[str, Any]] = {}

        for key, val in os.environ.items():
            if key.startswith("AURA_"):
                parts = key.lower().split("_")[1:]
                if len(parts) >= 2:
                    category = parts[0]
                    setting_name = "_".join(parts[1:])

                    if category not in overrides:
                        overrides[category] = {}

                    # Parse boolean/numeric primitives if applicable
                    parsed_val: Any = val
                    if val.lower() == "true":
                        parsed_val = True
                    elif val.lower() == "false":
                        parsed_val = False
                    else:
                        try:
                            parsed_val = float(val) if "." in val else int(val)
                        except ValueError:
                            parsed_val = val

                    overrides[category][setting_name] = parsed_val

        logger.info(f"Loaded {sum(len(v) for v in overrides.values())} environment variable overrides.")
        return overrides
