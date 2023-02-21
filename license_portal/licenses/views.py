from typing import Any
from urllib.request import Request

from django.http import HttpResponse
from django.views import View

from licenses.models import Client, License
from licenses.notifications import EmailNotification


# Create your views here.


class EmailRenderView(View):
    def get(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponse:
        # Take random objects
        client = Client.objects.last()
        license = License.objects.last()
        email_body, email_body_html = EmailNotification.render_templates(
            {"client": client, "expiring_licenses": [license]}
        )
        return HttpResponse(email_body_html)
