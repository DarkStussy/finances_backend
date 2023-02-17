class AssetException(Exception):
    def __init__(self, msg: str = 'Some currency exception'):
        self.message = msg
        super().__init__(msg)


class AssetExists(AssetException):
    def __init__(self, msg: str = 'Asset already exists'):
        self.message = msg
        super().__init__(msg)


class AssetNotFound(AssetException):
    def __init__(self, msg: str = 'Asset not found'):
        self.message = msg
        super().__init__(msg)
