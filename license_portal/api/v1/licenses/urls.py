from django.urls import re_path, include
from django.views.decorators.csrf import csrf_exempt

from api.v1.licenses.views import LicenseView

urlpatterns = (
    re_path(r"^license/", csrf_exempt(LicenseView.as_view()), name="license_view"),
)
