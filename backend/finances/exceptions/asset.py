from finances.exceptions.base import FinancesBaseException


class AssetException(FinancesBaseException):
    def __init__(self, msg: str = 'Some currency exception'):
        super().__init__(msg)


class AssetExists(AssetException):
    def __init__(self):
        super().__init__('Asset already exists')


class AssetNotFound(AssetException):
    def __init__(self):
        super().__init__('Asset not found')


class AssetCantBeDeleted(AssetException):
    def __init__(self):
        super().__init__('Asset cant be deleted')
