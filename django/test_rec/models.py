from django.db import models
import simplejson as json


class TmpUser(models.Model):
    MBTI = models.CharField(max_length=10, null=True, blank=True)
    ennear_ans = models.CharField(max_length=10, null=True, blank=True)
    ennear_res = models.CharField(max_length=10, null=True, blank=True)    
    prefer_movie_id = models.CharField(max_length=10, null=True, blank=True) #int로 안한 이유는 리스트로 담기 위함이다.
    recommended_character_id = models.CharField(max_length=10, null=True, blank=True)
    create_time = models.DateTimeField()

    def __str__(self):
        return int(self.id)