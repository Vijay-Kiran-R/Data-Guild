from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
import os

class TraceLogger:
    """
    Handles OpenTelemetry tracing and metrics logging.
    """
    def __init__(self, service_name="DataGuild"):
        """
        Initialize the TraceLogger.

        Args:
            service_name (str): The name of the service.
        """
        resource = Resource(attributes={
            "service.name": service_name
        })
        
        # Tracing
        self.trace_provider = TracerProvider(resource=resource)
        
        # Redirect traces to a file to keep CLI clean
        self.log_file = open(os.devnull, "w") 
        self.console_exporter = ConsoleSpanExporter(out=self.log_file)
        span_processor = SimpleSpanProcessor(self.console_exporter)
        self.trace_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(self.trace_provider)
        self.tracer = trace.get_tracer(service_name)

        # Metrics
        # Redirect metrics to the same file
        self.metric_exporter = ConsoleMetricExporter(out=self.log_file)
        metric_reader = PeriodicExportingMetricReader(self.metric_exporter)
        self.meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(self.meter_provider)
        self.meter = metrics.get_meter(service_name)
        
        self.token_counter = self.meter.create_counter(
            "llm_token_usage",
            description="Number of tokens used by LLM",
            unit="1"
        )
        self.latency_histogram = self.meter.create_histogram(
            "request_latency",
            description="Latency of LLM requests",
            unit="ms"
        )

    def get_tracer(self):
        """
        Returns the configured tracer.
        """
        return self.tracer

    def configure_logging(self, session_id: str):
        """
        Switch telemetry logging to a session-specific file.

        Args:
            session_id (str): The ID of the current session.
        """
        import os
        log_dir = "logs/telemetry_logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file_path = os.path.join(log_dir, f"{session_id}.log")
        
        # Open new file
        new_log_file = open(log_file_path, "a", encoding="utf-8")
        
        # Update exporters to use the new file
        # ConsoleSpanExporter and ConsoleMetricExporter store the stream in 'out'
        # We update the stream reference so future writes go to the new file
        self.console_exporter.out = new_log_file
        self.metric_exporter.out = new_log_file
        
        # Close the old file
        # We do this AFTER updating the exporters to minimize race conditions
        if hasattr(self, 'log_file') and self.log_file:
            try:
                self.log_file.close()
            except Exception:
                pass # Ignore errors if already closed
            
        self.log_file = new_log_file

# Global instance
trace_logger = TraceLogger()
tracer = trace_logger.get_tracer()

def configure_telemetry(session_id: str):
    """
    Configures telemetry for a specific session.

    Args:
        session_id (str): The ID of the session.
    """
    trace_logger.configure_logging(session_id)
