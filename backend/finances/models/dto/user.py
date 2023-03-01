from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from finances.models.enums.user_type import UserType


@dataclass
class User:
    id: UUID | None = None
    username: str | None = None
    user_type: UserType | None = None

    @classmethod
    def from_dict(cls, dct: dict) -> User:
        return User(
            id=dct.get('id'),
            username=dct.get('username'),
            user_type=UserType(dct.get('user_type'))
        )

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
