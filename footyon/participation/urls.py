from django.urls import path
from . import views

urlpatterns = [
    path('join/<int:match_id>/', views.join_match, name='join_match'),
    path('leave/<int:match_id>/', views.leave_match, name='leave_match'),
    path('no_show/<int:participation_id>/', views.mark_no_show, name='mark_no_show'),
    path('remove_no_show/<int:participation_id>/', views.remove_no_show, name='remove_no_show'),
    path('remove_participant/<int:participation_id>/', views.remove_participant, name='remove_participant'), # Soft remove participant
    path('<int:participation_id>/restore/', views.restore_participant, name='restore_participant'),
    path('<int:participation_id>/delete/', views.delete_participation, name='delete_participation'), # Permanently delete participation
    path('mark_present/<int:participation_id>/', views.mark_present, name='mark_present'),
    path('remove_present/<int:participation_id>/', views.remove_present, name='remove_present'),
]
