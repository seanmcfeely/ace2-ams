import alembic
import pytest

from alembic.config import Config
from sqlalchemy.orm import Session

from db.database import engine, get_db
from tests import factory


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """
    This fixture applies the Alembic database migrations at the beginning of a Pytest session and performs
    a downgrade (effectively removing all database tables) at the very end of the session.
    """

    config = Config("db/alembic.ini")

    alembic.command.downgrade(config, "base")
    alembic.command.upgrade(config, "head")

    session_db = next(get_db())

    # Add the default analysis modes since they are required to create a submission.
    factory.analysis_mode.create_or_read(value="default_alert", db=session_db)
    factory.analysis_mode.create_or_read(value="default_detect", db=session_db)
    factory.analysis_mode.create_or_read(value="default_event", db=session_db)
    factory.analysis_mode.create_or_read(value="default_response", db=session_db)

    # Add the default analysis statuses since they are required to create an analysis.
    factory.analysis_status.create_or_read(value="complete", db=session_db)
    factory.analysis_status.create_or_read(value="running", db=session_db)

    # Add the analyst user so API calls that create history entries have a valid user to link to.
    factory.user.create_or_read(username="analyst", db=session_db)

    session_db.commit()

    yield
    alembic.command.downgrade(config, "base")


@pytest.fixture()
def db():
    """
    This fixture creates a nested database transaction for each test that uses it. When the test is
    complete, the transaction is rolled back so that the database is in the same state as prior to the test.

    Most tests will not need to use this fixture directly, as they will use it indirectly via the client fixture.
    """

    # Connect to the database and begin a nested transaction.
    connection = engine.connect()
    connection.begin()
    session = Session(bind=connection)

    yield session

    # Close the session and the connection. The transaction is automatically rolled back.
    session.close()
    connection.close()
