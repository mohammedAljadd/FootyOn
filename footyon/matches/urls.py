from django.urls import path
from . import views

# This sets a namespace for this app's URLs.
# Using app_name allows us to refer to these URLs unambiguously in templates or views
# Example: {% url 'matches:manage' %} or redirect('matches:create_match')
app_name = 'matches'

urlpatterns = [
    # Admin: manage all matches
    path('manage/', views.manage_matches, name='manage'),
    path('create/', views.create_match, name='create_match'),
    path('<int:match_id>/', views.view_match, name='view_match'),
    path('<int:match_id>/edit/', views.edit_match, name='edit_match'),
    path('<int:match_id>/delete/', views.delete_match, name='delete_match'),
]
