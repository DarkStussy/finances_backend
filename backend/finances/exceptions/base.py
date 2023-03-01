class FinancesBaseException(Exception):
    def __init__(self, msg: str = 'Base exception'):
        self.message = msg
        super().__init__(msg)
