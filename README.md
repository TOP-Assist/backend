# TOP Assist Backend

This repository contains the backend to the TOP Assist text optimization tool.

- TODO: Add note about how if user specifies different analysis model in .env they need to download it; same goes for the container.

## Licensing

This project follows the [REUSE specification](https://reuse.software/) so that every file carries machine-readable copyright and license information in [SPDX](https://spdx.dev/) format. The project is licensed under the [AGPL 3.0 or later](LICENSES/AGPL-3.0-or-later.txt.); the full license texts are in `LICENSES/`.

The copyright is held jointly by deepsight GmbH and Bergische Universität Wuppertal. Every source file starts with a header like this:

```python
# SPDX-FileCopyrightText: 2026 deepsight GmbH
# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-License-Identifier: AGPL-3.0-or-later
```

Files that cannot contain comments (JSON, lock files, images, …) are covered by `REUSE.toml` in the repository root.

We use the [`reuse`](https://github.com/fsfe/reuse-tool) tool to add and check these headers. It can be run via `uvx` without installing it:

```bash
# add the header to new files
uvx reuse annotate \
  --copyright "deepsight GmbH" \
  --copyright "Bergische Universität Wuppertal" \
  --license AGPL-3.0-or-later \
  path/to/new_file.py

# check that every file in the repository has copyright and license information
uvx reuse lint
```

Run `uvx reuse lint` before opening a merge request; it must pass.
