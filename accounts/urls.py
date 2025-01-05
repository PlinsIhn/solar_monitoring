from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate_view, name='activate'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('channel/', views.channel_view, name='channel'),
    path('channels/delete/<int:channel_id>/', views.delete_channel, name='delete_channel'),
    path('historique/', views.historique_view, name='historique'),
    path('aide-support/', views.aide_support_view, name='aide_support'),
    path('channel-data/<int:channel_id>/', views.get_channel_data, name='channel_data'),
    path('api/receive-data/', views.receive_data, name='receive_data'),
]

