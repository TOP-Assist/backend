# SPDX-FileCopyrightText: 2026 Bergische Universität Wuppertal
# SPDX-FileCopyrightText: 2026 deepsight GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Integration of optional OpenTelemetry instrumentation."""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from importlib.metadata import version

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging.handler import LoggingHandler
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from backend.config import Settings


@contextmanager
def configure_telemetry(settings: Settings) -> Generator[None]:
    """
    Set up OpenTelemetry metrics, traces and logs, exported via OTLP.
    Must run after `configure_logging`, since `dictConfig` replaces the handlers
    of the root logger. All providers are flushed and shut down on exit.
    """
    resource = Resource.create(
        {
            SERVICE_NAME: settings.otel_service_name,
            SERVICE_VERSION: version("backend"),
        }
    )
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
        )
    )
    trace.set_tracer_provider(tracer_provider)

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[
            PeriodicExportingMetricReader(
                OTLPMetricExporter(
                    endpoint=settings.otel_exporter_otlp_endpoint
                )
            )
        ],
    )
    metrics.set_meter_provider(meter_provider)

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(endpoint=settings.otel_exporter_otlp_endpoint)
        ),
    )
    set_logger_provider(logger_provider)
    handler = LoggingHandler(logger_provider=logger_provider)
    root = logging.getLogger()
    root.addHandler(handler)
    try:
        yield
    finally:
        root.removeHandler(handler)
        logger_provider.shutdown()
        meter_provider.shutdown()
        tracer_provider.shutdown()


def instrument_mongodb() -> None:
    """
    Add OpenTelemetry instrumentation for PyMongo. Make sure to run this before
    creating an `AsyncMongoClient`.
    """
    PymongoInstrumentor().instrument()


def instrument_fastapi(app: FastAPI) -> None:
    """
    Add OpenTelemetry instrumentation to the given FastAPI app object.
    """
    FastAPIInstrumentor.instrument_app(app, excluded_urls="health")
