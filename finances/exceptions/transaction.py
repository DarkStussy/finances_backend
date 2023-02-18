class TransactionException(Exception):
    def __init__(self, msg: str = 'Some transaction exception'):
        self.message = msg
        super().__init__(msg)


class TransactionCategoryNotFound(Exception):
    def __init__(self, msg: str = 'Transaction category not found'):
        self.message = msg
        super().__init__(msg)


class TransactionCategoryExists(TransactionException):
    def __init__(self, msg: str = 'Transaction category already exists'):
        self.message = msg
        super().__init__(msg)
