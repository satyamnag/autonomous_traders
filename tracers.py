from agents import TracingProcessor, Trace, Span
import secrets
import string

ALPHANUM = string.ascii_lowercase + string.digits

def make_trace_id(tag: str) -> str:
    """
    Return a string of the form 'trace_<tag><random>',
    where the total length after 'trace_' is 32 chars.
    """
    tag += "0"
    pad_len = 32 - len(tag)
    random_suffix = ''.join(secrets.choice(ALPHANUM) for _ in range(pad_len))
    return f"trace_{tag}{random_suffix}"

class LogTracer(TracingProcessor):

    def get_name(self, trace_or_span: Trace | Span) -> str | None:
        trace_id = trace_or_span.trace_id
        if not trace_id.startswith("trace_"):
            return None
        name_part = trace_id[len("trace_"):]
        return name_part.split("0", 1)[0] or None

    def on_trace_start(self, trace) -> None:
        name = self.get_name(trace)
        if name:
            print(f"[TRACE][{name}] Started: {trace.name}")

    def on_trace_end(self, trace) -> None:
        name = self.get_name(trace)
        if name:
            print(f"[TRACE][{name}] Ended: {trace.name}")

    def on_span_start(self, span) -> None:
        name = self.get_name(span)
        span_type = span.span_data.type if span.span_data and hasattr(span.span_data, "type") else "span"
        if name:
            if not span.span_data:
                message = "Started span"
            else:
                message = "Started"
                if getattr(span.span_data, "type", None):
                    message += f" {span.span_data.type}"
                if getattr(span.span_data, "name", None):
                    message += f" {span.span_data.name}"
                if getattr(span.span_data, "server", None):
                    message += f" {span.span_data.server}"
            if span.error:
                message += f" ERROR: {span.error}"
            print(f"[SPAN][{name}][{span_type}] {message}")

    def on_span_end(self, span) -> None:
        name = self.get_name(span)
        span_type = span.span_data.type if span.span_data and hasattr(span.span_data, "type") else "span"
        if name:
            if not span.span_data:
                message = "Ended span"
            else:
                message = "Ended"
                if getattr(span.span_data, "type", None):
                    message += f" {span.span_data.type}"
                if getattr(span.span_data, "name", None):
                    message += f" {span.span_data.name}"
                if getattr(span.span_data, "server", None):
                    message += f" {span.span_data.server}"
            if span.error:
                message += f" ERROR: {span.error}"
            print(f"[SPAN][{name}][{span_type}] {message}")

    def force_flush(self) -> None:
        pass

    def shutdown(self) -> None:
        pass