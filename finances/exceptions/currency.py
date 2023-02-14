class CurrencyException(Exception):
    def __init__(self, msg: str = 'Some currency exception'):
        self.message = msg
        super().__init__(msg)


class CurrencyNotFound(CurrencyException):
    def __init__(self,
                 msg: str = 'Currency not found'):
        self.message = msg
        super().__init__(msg)
