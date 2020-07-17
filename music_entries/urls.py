from django.urls import path
from . import views

urlpatterns = [
    path('api/<str:key>/', views.MusicEntryListCreate),
    path('edit/<int:entry_id>/', views.edit),
    path('submit/l/', views.submit_link, name='submit-link'),
    path('submit/', views.submit, name='submit'),
    path('<str:key>/', views.view, name='view'),
    path('', views.view_own, name='view-own'),
]
