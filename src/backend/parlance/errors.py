# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Custom errors in the Parlance domain."""


class ParlanceNotFoundError(Exception):
    def __init__(self, domain: str) -> None:
        self.domain = domain
        super().__init__(f"No parlance found for domain: {domain}")
