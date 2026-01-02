import logging

import pytest

from smart_home.utils.logging import get_logger


@pytest.fixture(autouse=True)
def cleanup_logging():
    root_logger = logging.getLogger()

    # Reset BEFORE the test
    root_logger.handlers.clear()
    root_logger.setLevel(logging.NOTSET)

    yield  # Run the test where get_logger() will now execute fully

    # Reset AFTER the test
    root_logger.handlers.clear()
    root_logger.setLevel(logging.NOTSET)


def test_logger_is_correctly_configured():
    get_logger()
    log = logging.getLogger()

    # Check the default logger level
    assert log.level == int(logging.INFO)

    # Check handler type
    handler = log.handlers[0]
    assert isinstance(handler, logging.StreamHandler), (
        "Handler should be a StreamHandler."
    )

    # Check that format is set
    assert handler.formatter is not None


def test_logger_is_idempotent():
    """Tests that calling get_logger() twice does not add duplicate handlers."""
    logger_1 = get_logger()

    # 2 because of pytest
    assert len(logger_1.handlers) == 2

    logger_2 = get_logger()
    # no new handlers should be added
    assert len(logger_2.handlers) == 2, (
        "Should not add a second handler on second call (Idempotency check)."
    )
    assert logger_1 is logger_2, "Should return the same logger instance."
