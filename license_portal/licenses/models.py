""" Data model for licenses application
"""
import enum

from datetime import timedelta, datetime
from typing import Tuple, List

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

LICENSE_EXPIRATION_DELTA = timedelta(days=90)


class ChoiceEnum(enum.Enum):
    """Enum for choices in a choices field"""

    @classmethod
    def get_choices(cls) -> List[Tuple[int, str]]:
        return [(a.value, a.name) for a in cls]


class Package(ChoiceEnum):
    """A Package accessible to a client with a valid license"""

    javascript_sdk = 0
    ios_sdk = 1
    android_sdk = 2


class LicenseType(ChoiceEnum):
    """A license type"""

    production = 0
    evaluation = 1


class NotificationType(ChoiceEnum):
    """A notification type"""

    four_month = 0
    one_month = 1
    one_week = 2


def get_default_license_expiration() -> datetime:
    """Get the default expiration datetime"""
    return datetime.utcnow() + LICENSE_EXPIRATION_DELTA


class License(models.Model):
    """Data model for a client license allowing access to a package"""

    client = models.ForeignKey("Client", on_delete=models.CASCADE)
    package = models.PositiveSmallIntegerField(choices=Package.get_choices())
    license_type = models.PositiveSmallIntegerField(choices=LicenseType.get_choices())

    created_datetime = models.DateTimeField(auto_now=True)
    expiration_datetime = models.DateTimeField(default=get_default_license_expiration)


class Client(models.Model):
    """A client who holds licenses to packages"""

    client_name = models.CharField(max_length=120, unique=True)
    poc_contact_name = models.CharField(max_length=120)
    poc_contact_email = models.EmailField()

    admin_poc = models.ForeignKey(
        User, limit_choices_to={"is_staff": True}, on_delete=models.CASCADE
    )


class LicenseNotification(models.Model):
    notification = models.ForeignKey("Notification", on_delete=models.CASCADE)
    license = models.ForeignKey("License", on_delete=models.CASCADE)
    notification_type = models.PositiveSmallIntegerField(
        choices=NotificationType.get_choices()
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_notification_type(license: License) -> int:
        if license.expiration_datetime - timezone.now() > timedelta(days=32):
            notif_type = NotificationType.four_month.value
        elif license.expiration_datetime - timezone.now() < timedelta(days=7):
            notif_type = NotificationType.one_week.value
        else:
            notif_type = NotificationType.one_month.value
        return notif_type


class Notification(models.Model):
    client = models.ForeignKey("Client", on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
