from django.urls import path
from . import views

urlpatterns = [
    path('join/<int:match_id>/', views.join_match, name='join_match'),
    path('leave/<int:match_id>/', views.leave_match, name='leave_match'),
]
