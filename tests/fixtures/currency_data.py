from finances.models import dto


def get_test_currency() -> dto.Currency:
    return dto.Currency(
        id=1,
        name='test',
        code='TST',
        is_custom=False,
        rate_to_base_currency=None,
        user=None
    )
