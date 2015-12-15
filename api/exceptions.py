from rest_framework import status
from rest_framework.exceptions import APIException


class UnauthorizedAccess(APIException):
    """
        API raises this exception if request unauthorized
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Unauthorized Access."
