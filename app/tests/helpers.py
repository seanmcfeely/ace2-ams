from sqlalchemy.orm import Session

from core.auth import hash_password
from db.schemas.alert_queue import AlertQueue
from db.schemas.user import User
from db.schemas.user_role import UserRole


def create_test_user(db: Session, username: str, password: str):
    # Create an alert queue
    alert_queue = AlertQueue(value="test_queue")
    db.add(alert_queue)

    # Create a user role
    user_role = UserRole(value="test_role")
    db.add(user_role)

    # Create a user
    user = User(
        default_alert_queue=alert_queue,
        display_name="John Doe",
        email="john@test.com",
        password=hash_password(password),
        roles=[user_role],
        username=username,
    )
    db.add(user)
