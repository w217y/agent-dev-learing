import time
import logging
from contextlib import contextmanager

logging = logging.getLogger(__name__)

@contextmanager
def trace_step(run_id: str, step_name: str, metadata: dict | None = None):
    start = time.time()

    logging.info(
        "step_start",
        extra={
            "run_id": run_id,
            "step": step_name,
            "metadata": metadata or {},
        },
    )

    try:
        yield
    except Exception as e:
        logging.exception(
            "step_faild",
            extra={
                "run_id": run_id,
                "step": step_name,
                "error": str(e),
            },
        )
        raise
    finally:
        duration_ms = round((time.time()- start)*1000, 2)

        logging.info(
            "step_end",
            extra={
                "run_id": run_id,
                "step": step_name,
                "duration_ms": duration_ms,
            },
        )