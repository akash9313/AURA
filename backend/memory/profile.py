import logging
from datetime import datetime
from typing import Dict, List, Optional
from memory.models import ProfileFact
from memory.store import BaseMemoryRepository

logger = logging.getLogger("AURA.Memory.Profile")


class ProfileMemory:
    """
    Manages long-term user profile facts and preferences.

    STRICT PRINCIPLE: Only store facts explicitly requested by the user.
    """

    def __init__(self, repo: BaseMemoryRepository):
        self.repo = repo

    def save_fact(self, key: str, value: str, category: str = "preference") -> ProfileFact:
        """
        Save or overwrite an explicit user profile fact.

        Args:
            key (str): Unique attribute key (e.g. 'name', 'favorite_language').
            value (str): Fact value.
            category (str): Fact category ('preference', 'identity', 'skill', 'rule').

        Returns:
            ProfileFact: Saved ProfileFact instance.
        """
        fact = ProfileFact(
            key=key.strip().lower(),
            value=value.strip(),
            category=category.strip().lower(),
            updated_at=datetime.now()
        )
        self.repo.save_profile_fact(fact)
        logger.info(f"Saved ProfileMemory fact: '{fact.key}' = '{fact.value}'")
        return fact

    def get_fact(self, key: str) -> Optional[str]:
        """Get fact value by key."""
        fact = self.repo.get_profile_fact(key.strip().lower())
        return fact.value if fact else None

    def update_fact(self, key: str, value: str, category: str = None) -> Optional[ProfileFact]:
        """Update existing profile fact."""
        existing = self.repo.get_profile_fact(key.strip().lower())
        cat = category if category else (existing.category if existing else "preference")
        return self.save_fact(key, value, category=cat)

    def delete_fact(self, key: str) -> bool:
        """Delete an explicit profile fact by key."""
        k = key.strip().lower()
        success = self.repo.delete_profile_fact(k)
        if success:
            logger.info(f"Deleted ProfileMemory fact: '{k}'")
        return success

    def list_facts(self) -> Dict[str, str]:
        """List all stored user profile facts as a key-value dictionary."""
        facts = self.repo.list_profile_facts()
        return {fact.key: fact.value for fact in facts}
