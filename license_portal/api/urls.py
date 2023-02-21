from django.urls import re_path, include

urlpatterns = (
    re_path(r"^v1/", include(("api.v1.licenses.urls", "api.v1"), namespace="v1")),
)