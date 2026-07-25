from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Intent:

    name: str

    parameters: Dict[str, Any]

    confidence: float