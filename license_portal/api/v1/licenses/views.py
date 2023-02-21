from typing import Any

from django.db.models import QuerySet
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.licenses.serializers import NotificationSerializer
from licenses.models import Notification
from licenses.tasks import (
    check_for_expiring_licences,
)


class LicenseView(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = NotificationSerializer

    def get_queryset(self) -> QuerySet:
        """
        Return all notifications
        """
        return Notification.objects.all()

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Method to trigger check for license expiry
        """
        notifications = check_for_expiring_licences()
        serialized_notifications = self.get_serializer(
            self.get_queryset(), many=True
        ).data

        return Response(
            serialized_notifications,
            status=status.HTTP_201_CREATED,
        )
