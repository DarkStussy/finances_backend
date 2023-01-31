from dataclasses import dataclass
from uuid import UUID

from finances.models.enums.user_type import UserType


@dataclass
class User:
    id: UUID
    username: str
    user_type: UserType

    def add_password(self, hashed_password: str):
        return UserWithCreds(
            id=self.id,
            username=self.username,
            user_type=self.user_type,
            hashed_password=hashed_password
        )


@dataclass
class UserWithCreds(User):
    hashed_password: str | None = None

    def without_password(self) -> User:
        return User(
            id=self.id,
            username=self.username,
            user_type=self.user_type
        )
