import logging
from typing import Optional, Tuple
from cloud.accounts import AccountManager
from cloud.models import UserAccount
from cloud.sessions import SessionManager

logger = logging.getLogger("AURA.Cloud.Auth")


class AuthenticationEngine:
    """Authentication Orchestrator managing Sign Up, Sign In, and Token Validation."""

    def __init__(self, account_manager: AccountManager, session_manager: SessionManager):
        self.accounts = account_manager
        self.sessions = session_manager

    def sign_up(self, email: str, password: str) -> Tuple[UserAccount, str]:
        account = self.accounts.create_account(email, password)
        token = self.sessions.create_session(account.user_id)
        return account, token

    def sign_in(self, email: str, password: str) -> Tuple[UserAccount, str]:
        account = self.accounts.authenticate(email, password)
        if not account:
            raise PermissionError("Invalid email or password.")
        token = self.sessions.create_session(account.user_id)
        return account, token

    def verify_session(self, token: str) -> Optional[str]:
        return self.sessions.verify_token(token)
