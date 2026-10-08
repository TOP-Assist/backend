"""Custom errors in the Parlance domain."""


class ParlanceNotFoundError(Exception):
    def __init__(self, domain: str) -> None:
        self.domain = domain
        super().__init__(f"No parlance found for domain: {domain}")
