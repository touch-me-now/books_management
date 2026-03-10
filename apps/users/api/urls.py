from django.urls import path, include
from rest_framework_simplejwt.views import (
    token_obtain_pair,
    token_refresh,
    token_verify,
    token_blacklist
)

from .views import RegiterAPIView

token_urlpatterns = [
    path('', token_obtain_pair, name='token_obtain_pair'),
    path('refresh/', token_refresh, name='token_refresh'),
    path('verify/', token_verify, name='token_verify'),
    path('blacklist/', token_blacklist, name='token_blacklist'),
]

urlpatterns = [
    path('token/', include(token_urlpatterns)),
    path('register/', RegiterAPIView.as_view(), name="register"),
]
