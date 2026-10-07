import logging

from pymongo.errors import PyMongoError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class InvalidInputError(Exception):
    pass


def api_exception_handler(exc, context):
    if isinstance(exc, InvalidInputError):
        return _error_response(str(exc), status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, PyMongoError):
        logger.exception("Database error")
        return _error_response("Database is unavailable, please try again later",
                               status.HTTP_503_SERVICE_UNAVAILABLE)

    response = exception_handler(exc, context)
    if response is not None:
        detail = response.data.get("detail", response.data) if isinstance(response.data, dict) else response.data
        return _error_response(str(detail), response.status_code)

    logger.exception("Unhandled error")
    return _error_response("Something went wrong", status.HTTP_500_INTERNAL_SERVER_ERROR)


def _error_response(message: str, status_code: int) -> Response:
    return Response({"error": message}, status=status_code)
