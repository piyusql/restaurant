from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'booking.views.index'),
    url(r'^make_booking/$', 'booking.views.make_booking'),
    url(r'^api/', include('api.urls')),
    url(r'^release_booking/(.*)/$', 'booking.views.release_booking'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
