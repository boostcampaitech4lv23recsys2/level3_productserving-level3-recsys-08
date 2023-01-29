from django.urls import path, include
from . import views as views

app_name = 'test_rec'
urlpatterns = [
    path('start_test/', views.start_test, name='start_test'),
    path('mbti_test/', views.mbti_test, name='mbti_test'),
    path('enneagram_test/', views.enneagram_test, name='enneagram_test'),
    path('enneagram_test2', views.enneagram_test2, name='enneagram_test2'),
    path('enneagram_test3', views.enneagram_test3, name='enneagram_test3'),
    path('movie_test', views.movie_test, name='movie_test'),
    path('result_page', views.result_page, name='result_page'),
    path('result_movie/<int:character_id>', views.result_movie, name='result_movie'),

]