from functools import wraps
from flask import jsonify
import traceback


def error_to_json(error, description):
    return jsonify({
        "error": str(error),
        "description": str(description)
    })


def exception_to_json(exception):
    stacktrace = traceback.TracebackException.from_exception(exception).stack
    last_frame = stacktrace[-1]

    error_line = f': {last_frame.line}' if last_frame.line else ''

    return jsonify({
        "error": str(exception),
        "description": f'File "{last_frame.filename}", '
                       f'line {last_frame.lineno}{error_line}'
    })
