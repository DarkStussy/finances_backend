from finances.models import dto


def get_test_cryptocurrency() -> dto.CryptoCurrency:
    return dto.CryptoCurrency(
        id=1,
        name='Bitcoin',
        code='BTC'
    )


def get_test_cryptocurrency2() -> dto.CryptoCurrency:
    return dto.CryptoCurrency(
        id=2,
        name='Ethereum',
        code='ETH'
    )
