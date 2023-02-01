from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as views

app_name = 'common'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page="/"), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('delete_tmpuser/<int:tmpuser_id>/', views.delete_tmpuser, name='delete_tmpuser'),
]