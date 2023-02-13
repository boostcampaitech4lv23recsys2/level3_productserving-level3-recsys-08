from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as views
from .views import TmpUserDeleteView

app_name = 'common'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page="/"), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('detail_tmpuser/<int:tmpuser_id>/', views.detail_tmpuser, name='detail_tmpuser'),
    # path('delete_tmpuser/<int:tmpuser_id>/', views.delete_tmpuser, name='delete_tmpuser'),
    path('delete_tmpuser/<int:tmpuser_id>/', TmpUserDeleteView.as_view(), name='delete_tmpuser'),
    path('show_mbti_info/<str:mbti>/', views.show_mbti_info, name='show_mbti_info'),
    path('share_tmpuser/<int:tmpuser_id>/', views.share_tmpuser, name='share_tmpuser'),
]