
from django.urls import path
from . import views

urlpatterns = [

    path('registration/', views.registration, name='registration'),
    path('confirm-email/', views.confirm_email, name='confirm_email'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('', views.news_list, name='news_list'),
    path('news/<int:id>/', views.news_detail, name='news_detail'),
    path('news/create/', views.news_create, name='news_create'),
    path('news/<int:id>/edit/', views.news_update, name='news_update'),
    path('news/<int:id>/delete/', views.news_delete, name='news_delete'),
]
