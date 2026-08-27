import logging
from contextvars import ContextVar

# variable globale pour stocker le request_id par contexte
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="no-request-id")

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        return True