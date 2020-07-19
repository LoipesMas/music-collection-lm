from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'api'

router = routers.DefaultRouter()
router.register('users',UserViewSet)


urlpatterns = [
    path('auth/', obtain_auth_token),
    path('',include(router.urls)),
]