from finances.exceptions.base import FinancesBaseException


class CryptoAssetException(FinancesBaseException):
    def __init__(self, msg: str = 'Some crypto asset exception'):
        super().__init__(msg)


class CryptoAssetNotFound(CryptoAssetException):
    def __init__(self):
        super().__init__('Crypto asset not found')


class AddCryptoAssetError(CryptoAssetException):
    def __init__(self):
        super().__init__('Unable to add crypto asset')


class MergeCryptoAssetError(CryptoAssetException):
    def __init__(self):
        super().__init__('Unable to merge crypto asset')
