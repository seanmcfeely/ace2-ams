from pydantic import BaseSettings, Field, PostgresDsn


class Settings(BaseSettings):
    """
    Reads OS environment variables and maps them into attributes using Pydantic
    """

    database_url: PostgresDsn

    # Dictates whether or not the database is in testing mode, which is what controls if the database can be reset
    # during testing, such as during the GUI's end-to-end tests.
    in_testing_mode: bool = Field(default=False)

    # Whether or not to print SQL statements to the console
    sql_echo: bool = Field(default=False)

    default_analysis_mode_alert: str = Field(default="default_alert")
    default_analysis_mode_detect: str = Field(default="default_detect")
    default_analysis_mode_event: str = Field(default="default_event")
    default_analysis_mode_response: str = Field(default="default_response")


def get_settings():
    """
    Helper function to read the settings. Can be patched for unit testing.
    """

    return Settings()
