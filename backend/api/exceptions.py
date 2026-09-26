from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Let DRF create its normal error response first
    response = exception_handler(exc, context)

    # Customize permission-denied responses
    if response is not None and response.status_code == 403:
        response.data = {
            "detail": "Your current role does not have permission to access this resource."
        }

    # Return the response unchanged for other errors
    return response
