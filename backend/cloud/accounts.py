import hashlib
import logging
import uuid
from typing import Dict, Optional
from cloud.models import UserAccount

logger = logging.getLogger("AURA.Cloud.Accounts")


class AccountManager:
    """Manages user sign up, authentication profiles, and password hashing."""

    def __init__(self):
        self.accounts: Dict[str, UserAccount] = {}
        self.email_map: Dict[str, str] = {}

    def create_account(self, email: str, password: str) -> UserAccount:
        email_lower = email.lower()
        if email_lower in self.email_map:
            raise ValueError(f"Account with email '{email}' already exists.")

        user_id = f"usr_{uuid.uuid4().hex[:8]}"
        pwd_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

        account = UserAccount(user_id=user_id, email=email_lower, password_hash=pwd_hash)
        self.accounts[user_id] = account
        self.email_map[email_lower] = user_id

        logger.info(f"Created user account '{email_lower}' (ID: {user_id})")
        return account

    def authenticate(self, email: str, password: str) -> Optional[UserAccount]:
        user_id = self.email_map.get(email.lower())
        if not user_id:
            return None

        account = self.accounts.get(user_id)
        if not account:
            return None

        pwd_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if account.password_hash == pwd_hash:
            return account
        return None
