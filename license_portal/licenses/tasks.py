from datetime import datetime, timedelta
from typing import List

from celery import shared_task
from dateutil.relativedelta import relativedelta
from django.core.mail import send_mail as send_django_email
from django.db.models import Q, Exists, Subquery, OuterRef, Prefetch, QuerySet
from django.template.loader import get_template, render_to_string
from django.utils import timezone

from licenses.models import (
    License,
    Client,
    Notification,
    LicenseNotification,
    NotificationType,
)
from licenses.notifications import EmailNotification


def _get_time_conditions() -> Q:
    time_now = timezone.now()
    four_months_from_now = time_now + relativedelta(months=4)
    one_month_from_now = time_now + relativedelta(months=1)
    one_week_from_now = time_now + timedelta(days=7)

    four_months_from_now_qs = Q(
        expiration_datetime__lt=four_months_from_now + timedelta(days=1),
        expiration_datetime__gt=four_months_from_now - timedelta(days=1),
    ) & ~Q(licensenotification__notification_type=NotificationType.four_month.value)

    one_month_from_now_qs = Q(
        expiration_datetime__lt=one_month_from_now,
        expiration_datetime__gt=one_week_from_now,
    ) & ~Q(licensenotification__notification_type=NotificationType.one_month.value)

    within_a_week = Q(
        expiration_datetime__lte=one_week_from_now,
    ) & ~Q(licensenotification__notification_type=NotificationType.one_week.value)

    time_conditions = four_months_from_now_qs | within_a_week
    if timezone.now().weekday() == 0:
        time_conditions |= one_month_from_now_qs
    return time_conditions


def get_clients_with_expiring_licenses() -> QuerySet:
    time_conditions = _get_time_conditions()
    return (
        Client.objects.annotate(
            expiring_licenses_exist=Exists(
                Subquery(License.objects.filter(time_conditions, client=OuterRef("id")))
            )
        )
        .filter(expiring_licenses_exist=True)
        .prefetch_related(
            Prefetch(
                "license_set",
                queryset=License.objects.filter(time_conditions).distinct(),
                to_attr="expiring_licenses",
            )
        )
        .distinct()
    )


@shared_task()
def send_email(
    recipient_email: str, subject, email_body: str, email_body_html: str
) -> None:
    EmailNotification.send_notification([recipient_email], email_body, email_body_html)


def _create_notification(client) -> Notification:
    notification = Notification.objects.create(client=client)

    license_notifications = []
    for license in client.expiring_licenses:
        license_notifications.append(
            LicenseNotification(
                license=license,
                notification=notification,
                notification_type=LicenseNotification.get_notification_type(license),
            )
        )
    LicenseNotification.objects.bulk_create(license_notifications)
    return notification


@shared_task
def check_for_expiring_licences() -> List[Notification]:
    clients_with_expiring_licenses = get_clients_with_expiring_licenses()
    notifications = []

    for client in clients_with_expiring_licenses:
        email_body, email_body_html = EmailNotification.render_templates(
            {"client": client, "expiring_licenses": client.expiring_licenses}
        )
        notification = _create_notification(client)
        notifications.append(notification)
        send_email(
            client.poc_contact_email, "LICENSE EXPIRY", email_body, email_body_html
        )
    return notifications
