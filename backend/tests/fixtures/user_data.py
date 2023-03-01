from finances.models import dto
from finances.models.enums.user_type import UserType


def get_test_user() -> dto.User:
    return dto.User(
        username='morpheus',
        user_type=UserType.USER
    )
