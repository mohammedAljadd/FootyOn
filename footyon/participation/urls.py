from django.urls import path
from . import views

urlpatterns = [
    path('join/<int:match_id>/', views.join_match, name='join_match'),
    path('leave/<int:match_id>/', views.leave_match, name='leave_match'),
    path('no_show/<int:participation_id>/', views.mark_no_show, name='mark_no_show'),
    path('remove_no_show/<int:participation_id>/', views.remove_no_show, name='remove_no_show'),

]
