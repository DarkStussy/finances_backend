from _decimal import Decimal
from uuid import UUID

from finances.models import dto


def get_test_asset() -> dto.Asset:
    return dto.Asset(
        id=UUID('2a50f023-f4cc-43f0-b6e7-5f7503c2e846'),
        title='test asset',
        user_id=None,
        currency_id=None,
        amount=Decimal('10')
    )
