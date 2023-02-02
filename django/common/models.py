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