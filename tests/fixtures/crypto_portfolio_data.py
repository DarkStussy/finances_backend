from uuid import UUID

from finances.models import dto


def get_test_crypto_portfolio() -> dto.CryptoPortfolio:
    return dto.CryptoPortfolio(
        id=UUID('99e925f2-55fe-4236-844c-b714fc134b12'),
        title='test crypto portfolio',
        user_id=None
    )
