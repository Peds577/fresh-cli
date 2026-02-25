"""Configuration management for the Freshservice CLI."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration loader for Freshservice CLI."""

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        self.api_key = os.getenv("FRESHSERVICE_API_KEY")
        self.domain = os.getenv("FRESHSERVICE_DOMAIN", "freshservice.com")

    def load_from_env(self) -> bool:
        """Load configuration from environment variables.

        Returns:
            True if API key is present, False otherwise
        """
        self.api_key = os.getenv("FRESHSERVICE_API_KEY")
        self.domain = os.getenv("FRESHSERVICE_DOMAIN", "freshservice.com")
        return bool(self.api_key)

    def save_to_env(self, api_key: str, domain: str) -> None:
        """Save configuration to environment variables.

        Args:
            api_key: Freshservice API key
            domain: Freshservice domain
        """
        os.environ["FRESHSERVICE_API_KEY"] = api_key
        os.environ["FRESHSERVICE_DOMAIN"] = domain
        self.api_key = api_key
        self.domain = domain
