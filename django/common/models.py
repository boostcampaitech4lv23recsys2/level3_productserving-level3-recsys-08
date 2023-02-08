from django.db import models

# Create your models here.
from django.db import models
import simplejson as json
from django.contrib.auth.models import User


class UserINFO(models.Model):
    LoginUser = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='userinfo')
    index_page_characterIds = models.CharField(max_length=10000, null=True, blank=True)

    def __str__(self):
        return User.username



class BatchTrain(models.Model):
    LoginUser = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='batchtrain')
    model_name = models.CharField(max_length=30, null=True, blank=True)  
    model_path = models.CharField(max_length=300, null=True, blank=True)  
    recommended_movie_list = models.TextField(null=True, blank=True) #int로 안한 이유는 리스트로 담기 위함이다.
    create_time = models.DateTimeField()

    def __str__(self):
        return str(self.id)