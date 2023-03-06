class FinancesBaseException(Exception):
    def __init__(self, msg: str = 'Base exception'):
        self.message = msg
        super().__init__(msg)


class MergeModelError(FinancesBaseException):
    def __init__(self):
        super().__init__('Can\'t merge model')


class AddModelError(FinancesBaseException):
    def __init__(self):
        super().__init__('Can\'t create model')
