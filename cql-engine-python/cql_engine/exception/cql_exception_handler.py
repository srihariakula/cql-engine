"""
CQL Exception Handler

Handles uncaught exceptions in CQL engine threads.
"""

import sys
import traceback
from typing import Optional

from .cql_exception import CqlException


class CqlExceptionHandler:
    """
    Handler for uncaught exceptions in CQL engine threads.

    This handler can be used as a thread uncaught exception handler to
    catch and process exceptions that occur in worker threads.
    """

    def handle_uncaught_exception(
        self, thread: "threading.Thread", exc_type: type, exc_value: Exception, exc_traceback
    ) -> None:
        """
        Handle an uncaught exception in a thread.

        Args:
            thread: The thread in which the exception occurred
            exc_type: The type of the exception
            exc_value: The exception instance
            exc_traceback: The traceback object

        Raises:
            CqlException: Wraps the original exception with additional context
        """
        # Get root cause (the original exception if wrapped)
        root_cause = exc_value
        while root_cause.__cause__ is not None:
            root_cause = root_cause.__cause__

        # Print to stderr
        exc_info_str = "".join(
            traceback.format_exception(type(exc_value), exc_value, exc_traceback)
        )
        print(exc_info_str, file=sys.stderr)

        # Raise a CqlException with the stack trace
        error_message = (
            f"Unexpected exception caught during execution: {type(exc_value).__name__}\n"
            f"With trace:\n{exc_info_str}"
        )
        raise CqlException(error_message, cause=exc_value)
