from django.db import models


class TmpUser(models.Model):
    MBTI = models.CharField(max_length=10, null=True, blank=True)
    ennear_ans = models.CharField(max_length=10, null=True, blank=True)
    ennear_res = models.CharField(max_length=10, null=True, blank=True)    
    prefer_movie_id = models.IntegerField(null=True, blank=True)
    recommended_character_id = models.IntegerField(null=True, blank=True)
    create_time = models.DateTimeField()

    def __str__(self):
        return int(self.id)