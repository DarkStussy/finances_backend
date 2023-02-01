class UserException(Exception):
    def __init__(self, msg: str = 'Some user exception'):
        self.message = msg
        super().__init__(msg)


class UserExists(UserException):
    def __init__(self,
                 msg: str = 'This username is already in use by another user'):
        self.message = msg
        super().__init__(msg)


class UserNotFound(UserException):
    def __init__(self, msg: str = 'Incorrect username or password'):
        self.message = msg
        super().__init__(msg)
