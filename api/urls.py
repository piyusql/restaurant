from django.conf.urls import patterns, url

from api.handlers import Occupancy

urlpatterns = patterns('api.views',
                       url(r'^bookings/$', Occupancy.as_view()),
                       )
