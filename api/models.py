from django.db import models

from django.core.cache import cache

from django.db.models.signals import post_save

API_LOG_TYPE = ((1, 'Invalid IP'), (2, 'Bad Request'), (3, 'Request With Valid Response'))
REQUEST_TYPE_LIST = [('GET', 'GET'), ('POST', 'POST'), ('WebService', 'WebService')]
API_ALLOWED_IP_LIST_KEY = 'lms-api-valid-ip-list'
P_TYPE = ((1, 'Key Value Pair'), (2, 'JSON'),)


class IPAuthentication(models.Model):
    vendor_name = models.CharField(max_length=50)
    ip = models.CharField(max_length=15, unique=True)
    active = models.BooleanField(default=1)
    activated_on = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return "%(ip)s - %(activated_on)s" % (self.__dict__)


class ClientApi(models.Model):
    client = models.ForeignKey('sa_leadinfo.Client')
    order_ids = models.CommaSeparatedIntegerField(max_length=100)
    service_url = models.CharField(max_length=1000)
    request_type = models.CharField(max_length=25, choices=REQUEST_TYPE_LIST)
    format_string = models.TextField()
    parameter_type = models.PositiveSmallIntegerField(choices=P_TYPE, default=1)
    active = models.BooleanField(default=True)
    lead_extra_data = models.BooleanField()

    def __unicode__(self):
        return self.service_url


class APILog(models.Model):
    request_ip = models.CharField(max_length=15)
    log_type = models.PositiveSmallIntegerField(choices=API_LOG_TYPE)
    request_data = models.TextField()
    error = models.TextField(null=True, blank=True)
    handled = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.request_ip


class RedirectUrlPattern(models.Model):
    url_pattern = models.CharField(max_length=250, unique=True)
    redirect_url = models.CharField(max_length=250)
    is_active = models.BooleanField(default=1)

    def __unicode__(self):
        return self.url_pattern


def ipauthentication_post_save(instance, **kwargs):
    cache.delete(API_ALLOWED_IP_LIST_KEY)

post_save.connect(ipauthentication_post_save, sender=IPAuthentication)
