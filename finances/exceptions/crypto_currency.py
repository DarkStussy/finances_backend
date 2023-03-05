from finances.exceptions.base import FinancesBaseException


class CryptoCurrencyException(FinancesBaseException):
    def __init__(self, msg: str = 'Some crypto currency exception'):
        super().__init__(msg)


class CryptoCurrencyNotFound(CryptoCurrencyException):
    def __init__(self):
        super().__init__('Crypto currency not found')


class CryptoCurrencyExists(CryptoCurrencyException):
    def __init__(self):
        super().__init__('Crypto currency already exists')
