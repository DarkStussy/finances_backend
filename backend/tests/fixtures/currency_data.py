from finances.models import dto


def get_test_currency() -> dto.Currency:
    return dto.Currency(
        id=1,
        name='test',
        code='TST',
        is_custom=False,
        rate_to_base_currency=None,
        user_id=None
    )


def get_test_base_currency() -> dto.Currency:
    return dto.Currency(
        id=2,
        name='base',
        code='BTS',
        is_custom=False,
        rate_to_base_currency=None,
        user_id=None
    )
