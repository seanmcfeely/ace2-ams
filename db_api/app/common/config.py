"""
Environment variables / configuration
"""

import os

from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    """
    Reads OS environment variables and maps them into attributes using Pydantic
    """

    database_url: PostgresDsn
    database_test_url: PostgresDsn
    default_analysis_mode_alert: str = "default_alert"
    default_analysis_mode_detect: str = "default_detect"
    default_analysis_mode_event: str = "default_event"
    default_analysis_mode_response: str = "default_response"


def get_settings():
    """
    Helper function to read the settings. Can be patched for unit testing.
    """

    return Settings()


def is_in_testing_mode() -> bool:
    return "TESTING" in os.environ and os.environ["TESTING"].lower() == "yes"
