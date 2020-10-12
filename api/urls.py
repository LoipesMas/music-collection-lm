from django.urls import path, include
from rest_framework import routers
from . import views
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'api'

router = routers.DefaultRouter()

urlpatterns = [
    path('auth/', obtain_auth_token),
    path('parse/', views.ParseView.as_view()),
    path('userinfo/', views.UserInfoView.as_view()),
    path('submit/', views.MusicSubmit.as_view()),
    path('', include(router.urls)),
]
