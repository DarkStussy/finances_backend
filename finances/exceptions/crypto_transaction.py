from finances.exceptions.base import FinancesBaseException


class CryptoTransactionException(FinancesBaseException):
    def __init__(self, msg: str = 'Some crypto transaction exception'):
        super().__init__(msg)


class CryptoTransactionNotFound(CryptoTransactionException):
    def __init__(self):
        super().__init__('Crypto transaction not found')


class AddCryptoTransactionError(CryptoTransactionException):
    def __init__(self):
        super().__init__('Unable to add new crypto transaction')


class MergeCryptoTransactionError(CryptoTransactionException):
    def __init__(self):
        super().__init__('Unable to change crypto transaction')


class CryptoTransactionCantBeDeleted(CryptoTransactionException):
    def __init__(self):
        super().__init__('Crypto transaction cannot be deleted')
