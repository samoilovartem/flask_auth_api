from functools import wraps

from core.settings import settings
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_tracer(app):
    resource = Resource.create({SERVICE_NAME: settings.service_name})
    trace.set_tracer_provider(TracerProvider(resource=resource))

    jaeger_exporter = JaegerExporter(
        agent_host_name='jaeger',
        agent_port=6831,
    )

    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    FlaskInstrumentor().instrument_app(app)


def get_trace(function_name):
    def decorator(func):
        tracer = trace.get_tracer(__name__)

        @wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(function_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator
