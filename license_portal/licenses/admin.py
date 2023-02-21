from django.contrib import admin

from licenses.models import Client, License, Notification, LicenseNotification


class ClientAdmin(admin.ModelAdmin):
    list_display = ["client_name"]


class LicenseAdmin(admin.ModelAdmin):
    list_display = ["license_type", "client"]
    raw_id_fields = ["client"]


class NotificationAdmin(admin.ModelAdmin):
    list_display = ["client"]
    raw_id_fields = ["client"]


class LicenseNotificationAdmin(admin.ModelAdmin):
    list_display = ["license", "notification_type"]
    raw_id_fields = ["license", "notification"]


admin.site.register(Client, ClientAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(LicenseNotification, LicenseNotificationAdmin)
