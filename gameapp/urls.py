from django.urls import path
from gameapp import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('start_game/', views.start_game, name='start_game'),
    path("game/", views.game_view, name="game_view"),
    path("submit_guess/", views.submit_guess, name="submit_guess"),
    path('admin_panel/daily_report/', views.daily_report, name='daily_report'),
    path('admin_panel/user_report/', views.user_report, name='user_report'),
]
