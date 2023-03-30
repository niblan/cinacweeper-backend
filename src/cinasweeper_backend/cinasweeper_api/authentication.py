"""Manage google oauth"""
import re

import firebase_admin
from firebase_admin import auth, credentials


class AuthManager:
    """Manage the authentication of users"""

    def __init__(self) -> None:
        """Initialize the AuthManager"""
        self.cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(self.cred)

    def validate(self, email: str) -> bool:
        """Validate the email of a user

        Args:
            email (str): The email of the user

        Returns:
            bool: True if the email is fron ucu, False otherwise
        """
        return bool(re.match(r"^[a-z.]+\.pn@ucu\.edu\.ua$", email))

    def verify(self, token: str) -> dict[str, str] | None:
        """Verify a jwt token

        Args:
            token (str): The token to verify

        Returns:
            dict: The decoded token
        """
        try:
            user = auth.verify_id_token(token)
        except Exception:
            return None
        email = user["email"]
        if self.validate(email):
            return user
        return None

    def get_user(self, user_id: str) -> dict[str, str] | None:
        """Get a user from the database

        Args:
            user_id (str): The id of the user

        Returns:
            dict: The user
        """
        try:
            user = auth.get_user(user_id)
        except Exception:
            return None
        return user
