from finances.models import dto
from finances.models.enums.transaction_type import TransactionType


def get_test_transaction_category() -> dto.TransactionCategory:
    return dto.TransactionCategory(
        id=1,
        title='test_income',
        type=TransactionType.INCOME,
        user_id=None
    )
