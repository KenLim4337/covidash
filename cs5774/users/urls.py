from django.urls import path
from . import views

app_name= 'users' 

urlpatterns = [
    path('register',views.register, name='register'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('profile/<str:username>/edit', views.edit_user, name='edit-user'),
    path('remove-user', views.remove_user, name='remove-user'),
]
 