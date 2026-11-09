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

### Information on Environment Variables

The following is an overview of configuration variables, what they mean, and whether they are optional.
Please keep in mind that these lists are hard to keep up to date; if you find that a tweakable value is missing from this documentation, feel free to add it!

#### Observability

The following variables allow you to configure observability.

| Variable                   | Meaning                                                                     | Is optional? |
| -------------------------- | --------------------------------------------------------------------------- | ------------ |
| LOG_LEVEL                  | Which log severity gets logged. Configures both console and OTEL log level. | Yes          |
| OTEL_SERVICE_NAME          | Under which name the service reports its telemetry to the TLP endpoint.     | Yes          |
| OTEL_EXPORTER_TLP_ENDPOINT | Where to report metrics to. If left empty, telemetry will be disabled.      | Yes          |

#### Data Persistence

The following variables allow you to configure data persistence; their values may depend on values dictated by your deployed infrastructure.

| Variable         | Meaning                                             | Is optional? |
| ---------------- | --------------------------------------------------- | ------------ |
| MONGODB_HOST     | Name of host running MongoDB.                       | No           |
| MONGODB_PORT     | Port of MongoDB on given host. Defaults to `27017`. | Yes          |
| MONGODB_USERNAME | Username for MongoDB connection.                    | No           |
| MONGODB_PASSWORD | Password for MongoDB connection.                    | No           |
| MONGODB_DATABASE | MongDB database in which to write/read collections. | No           |

#### Language Processing

The following variables allow you to configure components around language processing; barrier analysis-relevant components are prefixed with `ANALYSIS`, translation-relevant components are prefixed with `LLM`.

| Variable             | Meaning                                                                                                                                                 | Is optional? |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| ANALYSIS_NUM_WORKERS | The number of workers (per fastAPI worker) that perform barrier analysis. Defaults to `1`.                                                              | Yes          |
| ANALYSIS_MODEL       | Which `spacy` model to use as the NLP backend for barrier analysis. Keep in mind that these are language-specific. Defaults to `de_dep_news_trf`.       | Yes          |
| LLM_BASE_URL         | The URL under which your OpenAI-compatible API is reachable.                                                                                            | No           |
| LLM_API_KEY          | The API key with which to send inference requests to `LLM_BASE_URL`.                                                                                    | No           |
| LLM_MODEL            | The model to use for inference.                                                                                                                         | No           |
| LLM_PROMPT_VARIANT   | Which variation of the TOP Assist prompt to use. Useful for maintaining different model-specific prompts. Defaults to `default`, if you can believe it. | Yes          |
| LLM_TEMPERATURE      | The temperature with which to execute inference. Defaults to `0.0`.                                                                                     | Yes          |
| LLM_TIMEOUT_SECONDS  | How many seconds to wait for a response from an inference server before terminating the request. Defaults to `60`.                                      | Yes          |
| LLM_MAX_RETRIES      | How often to retry an inference request on failure. Defaults to `0`.                                                                                    | Yes          |

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

## Container Image Releases

Releases are made from git tags of the form `vX.Y.Z` (e.g. `v1.2.0`), which are the single source of truth for the version:

- The Python package version is derived from it by [uv-dynamic-versioning](https://github.com/ninoseki/uv-dynamic-versioning).
  `pyproject.toml` deliberately contains no version, so please do not add one.
  Untagged commits get development versions such as `1.2.1.dev3+1a2b3c4`; run `uvx uv-dynamic-versioning` to print the version of your checkout.
- The container image is tagged with the version **without** the `v` prefix, i.e. `v1.2.0` is published as `docker.io/inbap/top-assist-backend:1.2.0`.

To publish a release, tag the commit and push the tag:

```bash
git tag -a v1.2.0
git push origin v1.2.0
```

The GitLab pipeline (`.gitlab-ci.yml`) then builds the image (with SBOM and provenance attestations and reproducible timestamps) and pushes it to Docker Hub.

### Building images locally

**GitLab builds release tags only.**
Our GitLab hosts have asked us to be mindful of storage and compute, so there are no pipelines for branches or merge requests.
Please build and test images on your own machine instead:

```bash
podman build -f Containerfile \
  --build-arg VERSION="$(uvx uv-dynamic-versioning)" \
  -t top-assist-backend:dev .
```

Omitting `VERSION` is fine for quick tests; the package version then defaults to `0.0.0+local`.

Should the pipeline be unavailable, a maintainer may publish a release by hand with the same build command CI uses.
Run it from a clean checkout of the release tag, as it pushes straight to Docker Hub:

```bash
TAG=v1.2.0
VERSION="${TAG#v}"
git switch --detach "$TAG"

# One-time: create a builder that supports attestations.
docker buildx create --name attest --driver docker-container

docker buildx build -f Containerfile \
  --builder attest \
  --platform linux/amd64 \
  --sbom=true --provenance=mode=max \
  --build-arg SOURCE_DATE_EPOCH="$(git log -1 --pretty=%ct)" \
  --build-arg VERSION="$VERSION" \
  --label org.opencontainers.image.version="$VERSION" \
  --label org.opencontainers.image.revision="$(git rev-parse HEAD)" \
  --label org.opencontainers.image.source="https://git.uni-wuppertal.de/top-assist/backend" \
  --output type=registry,rewrite-timestamp=true \
  --tag docker.io/inbap/top-assist-backend:"$VERSION" \
  .
```

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
