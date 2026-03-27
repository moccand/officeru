import logging
import time


access_logger = logging.getLogger('access')


class AccessLogMiddleware:
    """Log each HTTP request/response pair into acces.log."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started_at = time.perf_counter()
        response = self.get_response(request)
        duration_ms = int((time.perf_counter() - started_at) * 1000)

        access_logger.debug(
            '%s "%s %s" %s %dms',
            request.META.get('REMOTE_ADDR', '-'),
            request.method,
            request.get_full_path(),
            response.status_code,
            duration_ms,
        )
        return response
