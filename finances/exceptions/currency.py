from finances.exceptions.base import FinancesBaseException


class CurrencyException(FinancesBaseException):
    def __init__(self, msg: str = 'Some currency exception'):
        super().__init__(msg)


class CurrencyNotFound(CurrencyException):
    def __init__(self):
        super().__init__('Currency not found')


class CurrencyCantBeBase(CurrencyException):
    def __init__(self):
        super().__init__('Currency cannot be base')
