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
    path('channel-data/<int:channel_id>/', views.get_channel_data, name='channel_data'),
    path('api/receive_data/', views.receive_data, name='receive_data'),
    path('api/latest_data/<str:channel_name>/', views.get_latest_data, name='latest_data'),
    path("add-test-data/", views.test_graph, name="test_graph"),
    path('get-latest-temperature/', views.get_latest_temperature, name="get_latest_temperature"),
    path('historique/', views.historique, name='historique'),
    path('aide-support/', views.aide_support, name='aide_support'),
]


