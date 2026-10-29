# TOP Assist Backend

This repository contains the backend to the TOP Assist text optimization tool.

- TODO: Add note about how if user specifies different analysis model in .env they need to download it; same goes for the container.

## Setup

This project is [uv](https://docs.astral.sh/uv)-managed.
We ship an example environment file (`.env.example`), based on which you may create a `.env` file and fill out relevant variables.
Please note that the application will not launch without a properly provided `.env` file.

**Keep in mind** that - should you wish to experiment with other models for barrier analysis - you need to first install the relevant spaCy model for your environment.

### Running natively

You may get started by running

```bash
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Please note that you will need a `mongodb` instance for the service to talk to.

### Running in container

You may run the application using a container backend of your choice (e.g. Docker or podman).
The following documentation uses `podman` as an example but the Docker and podman API surfaces are identical for the use cases described below.

```bash
# Build the actual service image.
podman compose build

# Launch a complete stack, including the database dependency.
podman compose up -d
```

Note that - while we do set some environment variables in `compose.yml` - you will still need a `.env` file containing **your access data for a suitable LLM inference provider**.
This is done in order to avoid leaking API keys into version control.
**Please do not write your API keys into our `compose.yml` file.**

---

## Telemetry

This service supports push-based telemetry (traces, metrics and logs) via OTLP over gRPC.
Telemetry is enabled by setting `OTEL_EXPORTER_OTLP_ENDPOINT` to the gRPC endpoint of your OpenTelemetry collector, including the scheme (e.g. `http://collector:4317` for plaintext, `https://...` for TLS).
`OTEL_SERVICE_NAME` sets the service name reported to the collector (default: `top-assist-backend`).
Further `OTEL_*` variables (e.g. `OTEL_EXPORTER_OTLP_HEADERS`) are read by the OpenTelemetry SDK from the process environment only, not from `.env`.

The `compose.yml` stack includes a Grafana LGTM container for local exploration.
Grafana is available at http://localhost:3000; use _Explore_ with the Tempo (traces), Prometheus (metrics) or Loki (logs) data source.
The OTLP port `4317` is published on `127.0.0.1` only, so a natively running backend can report to it via `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`.

---

## Tips for running the service productively

### Right-size your workers

Keep in mind that barrier analysis has its own worker pool, each with a somewhat chunky transformer-based spaCy model loaded into RAM.
Moreover, **each fastAPI worker has its own barrier analysis worker pool**.
This means that _n_ fastAPI workers with _m_ barrier analysis workers will lead to _n * m_ spaCy models loaded into RAM.
Adjust your configuration to avoid extraneous RAM usage.

### Separate service from observability

Do not run the OTel stack on the same (virtual) machine as your productive server.
**The provided compose file is not meant for a production environment.**
You will want to avoid having your productive service compete for memory with the service you have set up to monitor your productive service.

---

## Licensing

This project follows the [REUSE specification](https://reuse.software/) so that every file carries machine-readable copyright and license information in [SPDX](https://spdx.dev/) format. The project is licensed under the [AGPL 3.0 or later](LICENSES/AGPL-3.0-or-later.txt); the full license texts are in `LICENSES/`.

The copyright is held jointly by deepsight GmbH and Bergische Universität Wuppertal. Every source file starts with a header like this:

```python
# SPDX-FileCopyrightText: 2026 deepsight GmbH
# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-License-Identifier: AGPL-3.0-or-later
```

Files that cannot carry such a header are annotated in `REUSE.toml` instead. This applies to generated files (`uv.lock`), tool configuration without comment support (`.python-version`) and the LLM prompts in `src/backend/translation/prompts/`, which are sent to the model verbatim and must therefore not contain a header.

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

Please remember to annotate all files with SPDX headers (or add them to `REUSE.toml`) before committing.
