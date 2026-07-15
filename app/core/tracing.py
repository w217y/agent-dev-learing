import time
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def trace_step(run_id: str, step_name: str, metadata: dict | None = None):
    start = time.time()

    logger.info(
        "step_start | run_id=%s | step=%s | metadata=%s",
        run_id,
        step_name,
        metadata or {},
    )

    try:
        yield
    except Exception as e:
        logger.exception(
            "step_failed | run_id=%s | step=%s | error=%s",
            run_id,
            step_name,
            str(e),
        )
        raise
    finally:
        duration_ms = round((time.time() - start) * 1000, 2)
        logger.info(
            "step_end | run_id=%s | step=%s | duration_ms=%s",
            run_id,
            step_name,
            duration_ms,
        )