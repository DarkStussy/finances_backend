from backend.finances.exceptions.base import FinancesBaseException


class UserException(FinancesBaseException):
    def __init__(self, msg: str = 'Some user exception'):
        super().__init__(msg)


class UserExists(UserException):
    def __init__(self):
        super().__init__('This username is already in use by another user')


class UserNotFound(UserException):
    def __init__(self):
        super().__init__('Incorrect username or password')
