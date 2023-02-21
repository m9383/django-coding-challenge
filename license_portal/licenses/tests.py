import uuid
from datetime import timedelta
from unittest.mock import patch, Mock

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from licenses.models import (
    Client,
    License,
    LicenseType,
    Package,
    LicenseNotification,
    Notification,
)
from licenses.tasks import (
    check_for_expiring_licences,
    get_clients_with_expiring_licenses,
)


class LicenseExpiryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user_a = User.objects.create(username="User A")
        cls.user_b = User.objects.create(username="User B")
        cls.client_a = Client.objects.create(
            client_name="Client A",
            poc_contact_name="Client Admin A",
            poc_contact_email=f"test.clienta@{uuid.uuid4().hex}.com",
            admin_poc=cls.user_a,
        )
        cls.client_b = Client.objects.create(
            client_name="Client B",
            poc_contact_name="Client Admin B",
            poc_contact_email=f"test.clientb@{uuid.uuid4().hex}.com",
            admin_poc=cls.user_b,
        )

    def init_licenses(self) -> None:
        time_now = timezone.now()
        four_months_from_now = time_now + relativedelta(months=4)
        one_month_from_now = time_now + relativedelta(months=1) - timedelta(hours=1)
        one_week_from_now = time_now + timedelta(days=6)
        five_months_from_now = time_now + relativedelta(months=5)

        self.expiring_license_a1 = License.objects.create(
            license_type=LicenseType.production.value,
            package=Package.ios_sdk.value,
            expiration_datetime=four_months_from_now,
            client=self.client_a,
        )
        self.expiring_license_a2 = License.objects.create(
            license_type=LicenseType.production.value,
            package=Package.android_sdk.value,
            expiration_datetime=one_month_from_now,
            client=self.client_a,
        )
        self.expiring_license_a3 = License.objects.create(
            license_type=LicenseType.production.value,
            package=Package.javascript_sdk.value,
            expiration_datetime=one_week_from_now,
            client=self.client_a,
        )
        self.expiring_license_b1 = License.objects.create(
            license_type=LicenseType.production.value,
            package=Package.ios_sdk.value,
            expiration_datetime=five_months_from_now,
            client=self.client_b,
        )

    @patch("licenses.tasks.send_email")
    @freeze_time("2023-02-18T15:00")
    def test_expiry_logic_nonmonday(self, send_email: Mock) -> None:
        self.init_licenses()
        clients = get_clients_with_expiring_licenses()
        self.assertEqual(clients.count(), 1)
        self.assertEqual(len(clients[0].expiring_licenses), 2)

        check_for_expiring_licences()
        self.assertEqual(send_email.call_count, 1)
        self.assertEqual(LicenseNotification.objects.count(), 2)
        self.assertEqual(Notification.objects.count(), 1)

        # Expect it not to be sent again
        check_for_expiring_licences()
        self.assertEqual(send_email.call_count, 1)
        self.assertEqual(LicenseNotification.objects.count(), 2)
        self.assertEqual(Notification.objects.count(), 1)

        # Change from license A2 to one week, expect second email
        self.expiring_license_a2.expiration_datetime = (
            self.expiring_license_a3.expiration_datetime
        )
        self.expiring_license_a2.save()

        check_for_expiring_licences()
        self.assertEqual(send_email.call_count, 2)
        self.assertEqual(LicenseNotification.objects.count(), 3)
        self.assertEqual(Notification.objects.count(), 2)

    @patch("licenses.tasks.send_email")
    @freeze_time("2023-02-20T15:00")
    def test_expiry_logic_monday(self, send_email: Mock) -> None:
        self.init_licenses()
        clients = get_clients_with_expiring_licenses()
        self.assertEqual(clients.count(), 1)
        self.assertEqual(len(clients[0].expiring_licenses), 3)

        check_for_expiring_licences()
        self.assertEqual(send_email.call_count, 1)
        self.assertEqual(LicenseNotification.objects.count(), 3)
        self.assertEqual(Notification.objects.count(), 1)

        # Expect it not to be sent again
        check_for_expiring_licences()
        self.assertEqual(send_email.call_count, 1)
        self.assertEqual(LicenseNotification.objects.count(), 3)
        self.assertEqual(Notification.objects.count(), 1)
