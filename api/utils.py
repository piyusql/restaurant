import sys
import copy
import json
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login
from django.core.cache import cache

from api.exceptions import UnauthorizedAccess
from api.models import IPAuthentication, APILog, API_ALLOWED_IP_LIST_KEY

from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

ERROR_CODES = dict((
    (001, "IP Not Authorized."),
    (002, "Invalid Authentication."),
    (003, "Bad Data Format."),
))


def simpleauth(func):
    """
    Simple authentication and login for GET api.
    Serves as a decorator function.

    @param : Func that it decorates.
    @returns : an inner function that does additional
               authentication.
    """

    def inner(self, request):
        username = request.REQUEST.get("username", None)
        password = request.REQUEST.get("password", None)

        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return func(self, request)
        else:
            return Response(ERROR_CODES.get(002))
    return inner


def ip_authenticator(func):
    """
    A decorator function that implements the ip-authentication
    for GET/POST requests.

    @param: Function that it decorates.
    @returns: an inner function that does additional
              authentication
    """

    def inner(self, request):
        request_host = request.META["REMOTE_ADDR"]
        valid_host = cache.get(API_ALLOWED_IP_LIST_KEY)
        if not valid_host:
            valid_host = IPAuthentication.objects.filter(active=1).values_list('ip', flat=True)
            cache.set(API_ALLOWED_IP_LIST_KEY, valid_host, 1 * 60 * 60)
        # check if ip is listed in valid list, if not then check for request throttle limit within timeframe
        if not (request_host in valid_host) and is_ip_throttled(request_host):
            api_log_entry(request, ERROR_CODES.get(001), 1)
            raise UnauthorizedAccess
        return func(self, request)
    return inner


def get_post_dict(request):
    """
    A simple utility function to get the POST parameters

    @param request : The HTTPRequest object sent to the URL.
    @returns dictionary of parameters
    """
    try:
        post_dict = json.loads(request.REQUEST.get("data", ""))
    except (IndexError, TypeError, ValueError):
        return None
    else:
        return post_dict


def is_ip_throttled(request_ip, timeout=30):
    """
        This method check whether a request came from the same ip in last 30 seconds.
        you can call this method with your convenient timeout parameter.
    """
    _key = 'latest_request_ip_list_for_api_call'
    ip_list = cache.get(_key, {})
    for _ip, _time in copy.copy(ip_list).iteritems():
        if _time < (datetime.now() - timedelta(seconds=timeout)):
            del ip_list[_ip]
    if request_ip in ip_list:
        return True
    ip_list[request_ip] = datetime.now()
    # set the change list for next 15 minutes
    cache.set(_key, ip_list, 15 * 60)
    return False


def api_log_entry(request, error=None, _type=1):
    """
        makes an api log as request data and the related error    
    """
    APILog.objects.create(log_type=_type, request_ip=request.META['REMOTE_ADDR'],
                          request_data=json.dumps(request.POST or request.GET), error=str(error))
