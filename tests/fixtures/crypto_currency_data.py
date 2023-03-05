from finances.models import dto


def get_test_cryptocurrency() -> dto.CryptoCurrency:
    return dto.CryptoCurrency(
        id=1,
        name='Bitcoin',
        code='BTC'
    )
