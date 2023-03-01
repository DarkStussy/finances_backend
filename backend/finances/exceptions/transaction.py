from backend.finances.exceptions.base import FinancesBaseException


class TransactionException(FinancesBaseException):
    def __init__(self, msg: str = 'Some transaction exception'):
        super().__init__(msg)


class AddTransactionError(TransactionException):
    def __init__(self):
        super().__init__('Unable to add new transaction')


class MergeTransactionError(TransactionException):
    def __init__(self):
        super().__init__('Unable to change transaction')


class TransactionNotFound(TransactionException):
    def __init__(self):
        super().__init__('Transaction not found')


class TransactionCategoryNotFound(TransactionException):
    def __init__(self):
        super().__init__('Transaction category not found')


class TransactionCategoryExists(TransactionException):
    def __init__(self):
        super().__init__('Transaction category already exists')


class TransactionCantBeChanged(TransactionException):
    def __init__(self, msg: str = 'Transaction cannot be changed'):
        super().__init__(msg)


class TransactionCantBeDeleted(TransactionException):
    def __init__(self):
        super().__init__('Transaction cannot be deleted')
