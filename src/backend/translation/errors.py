"""Custom errors in the translation domain."""


class TranslationError(Exception):
    """Base class for expected translation failures."""


class TranslationTimeoutError(TranslationError):
    pass


class TranslationUnavailableError(TranslationError):
    pass


class TranslationProviderError(TranslationError):
    pass


class TranslationOutputError(TranslationError):
    pass
