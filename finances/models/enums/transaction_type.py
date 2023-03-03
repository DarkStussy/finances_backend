from enum import Enum


class TransactionType(Enum):
    INCOME = 'income'
    EXPENSE = 'expense'


class CryptoTransactionType(Enum):
    BUY = 'buy'
    SELL = 'sell'
