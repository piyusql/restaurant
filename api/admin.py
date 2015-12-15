from django.contrib import admin

from api.models import APILog, IPAuthentication, ClientApi, RedirectUrlPattern


class IPAuthenticationAdmin(admin.ModelAdmin):
    list_display = ('vendor_name', 'ip', 'active', 'activated_on')
    list_filter = ('active',)
    search_fields = ('vendor_name',)

    class Meta:
        model = IPAuthentication


class APILogAdmin(admin.ModelAdmin):
    list_display = ('request_ip', 'log_type', 'handled', 'request_data', 'error', 'timestamp')
    list_filter = ('log_type', 'timestamp',)
    search_fields = ('request_ip', 'request_data')
    actions = ['try_saving_leads', 'mark_unhandled']

    class Meta:
        model = APILog

    def mark_unhandled(self, request, queryset):
        n = queryset.update(handled=0)
        return self.message_user(request, "selected %d logs marked un-handled." % (n))

    def try_saving_leads(self, request, queryset):
        n = queryset.update(handled=1)
        s = 4  # save_leads(queryset)
        return self.message_user(request, "selected %d logs tried and %d new leads inserted." % (n, s))


class ClientApiAdmin(admin.ModelAdmin):
    list_display = ('service_url', 'order_ids', 'request_type', 'parameter_type', 'active',)
    list_filter = ('request_type', 'active')
    search_fields = ('service_url', 'order_ids',)
    actions = ['activate_apis', 'de_activate_apis']

    class Meta:
        model = ClientApi

    def activate_apis(self, request, queryset):
        n = queryset.update(active=1)
        return self.message_user(request, "selected %d apis activated." % (n))

    def de_activate_apis(self, request, queryset):
        n = queryset.update(active=0)
        return self.message_user(request, "selected %d apis de-activated." % (n))


class RedirectUrlPatternAdmin(admin.ModelAdmin):
    list_display = ('url_pattern', 'redirect_url', 'is_active',)
    list_filter = ('is_active',)
    search_fields = ('url_pattern', 'redirect_url',)

    class Meta:
        model = RedirectUrlPattern

admin.site.register(ClientApi, ClientApiAdmin)
admin.site.register(APILog, APILogAdmin)
admin.site.register(IPAuthentication, IPAuthenticationAdmin)
admin.site.register(RedirectUrlPattern, RedirectUrlPatternAdmin)
