from rest_framework import serializers

from licenses.models import Notification, Client, LicenseNotification


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["client_name"]


class NotificationSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    expiring_license_count = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ["client", "expiring_license_count", "created"]

    def get_expiring_license_count(self, obj: Notification) -> int:
        return obj.licensenotification_set.all().count()
