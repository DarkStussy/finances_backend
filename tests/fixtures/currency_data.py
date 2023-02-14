from _decimal import Decimal

from finances.models import dto


def get_test_currency() -> dto.Currency:
    return dto.Currency(
        name='test',
        code='TST',
        rate_to_base_currency=Decimal('0.1'),
    )
