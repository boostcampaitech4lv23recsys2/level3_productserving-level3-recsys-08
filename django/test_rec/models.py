from django.db import models
import simplejson as json
from django.contrib.auth.models import User


class TmpUser(models.Model):
    LoginUser = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tmpuser')
    MBTI = models.CharField(max_length=10, null=True, blank=True)
    ennea_ans1 = models.CharField(max_length=10, null=True, blank=True)
    ennea_ans2 = models.CharField(max_length=10, null=True, blank=True)
    ennea_res = models.CharField(max_length=10, null=True, blank=True)    
    prefer_movie_id = models.TextField(null=True, blank=True) #int로 안한 이유는 리스트로 담기 위함이다.
    recommended_character_id = models.TextField(null=True, blank=True)
    fit_character_id = models.TextField(null=True, blank=True)
    recommended_character_sim = models.TextField(null=True, blank=True)
    fit_character_sim = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField()

    def __str__(self):
        return str(self.id)