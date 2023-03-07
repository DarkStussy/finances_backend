from _decimal import Decimal
from datetime import datetime

from finances.models import dto
from finances.models.enums.transaction_type import CryptoTransactionType


def get_test_crypto_transaction() -> dto.CryptoTransaction:
    return dto.CryptoTransaction(
        id=1,
        user_id=None,
        portfolio_id=None,
        crypto_asset_id=None,
        type=CryptoTransactionType.BUY,
        amount=Decimal('5'),
        price=Decimal('5.12'),
        created=datetime.now()
    )
