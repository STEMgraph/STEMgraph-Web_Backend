import time
import logging

logger = logging.getLogger("api")

async def logging_middleware(request, call_next):
    start = time.time()

    response = await call_next(request)
    duration = (time.time() - start) * 1000

    logger.info(
        f"{request.method} {request.url.path}",
        {
            "status": response.status_code,
            "duration_ms": round(duration, 2),
            "params": dict(request.query_params)
        }
    )

    return response
