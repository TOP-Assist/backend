# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

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
