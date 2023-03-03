from finances.exceptions.base import FinancesBaseException


class CryptoPortfolioException(FinancesBaseException):
    def __init__(self, msg: str = 'Some crypto portfolio exception'):
        super().__init__(msg)


class CryptoPortfolioExists(FinancesBaseException):
    def __init__(self):
        super().__init__('Crypto portfolio already exists')


class CryptoPortfolioNotFound(FinancesBaseException):
    def __init__(self):
        super().__init__('Crypto portfolio not found')
