from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    # Admin: manage all matches
    path('manage/', views.manage_matches, name='manage'),
]
