from django.db import models
from django.contrib.auth.models import User
from main.models import AnswersForFromSelf, AnswersForFromUs
from member.models import UserInfo

# Create your models here.
class Challenge(models.Model):
    objects = models.Manager()

    host = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name='host', null=True, blank=True)
    co_host = models.ManyToManyField(UserInfo, related_name='cohosts', blank=True)
    day = models.IntegerField()
    start_date = models.DateField(auto_now_add=False)
    end_date = models.DateField(auto_now_add=False)
    title = models.CharField(max_length=30, null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    participant = models.ManyToManyField(UserInfo, related_name='participant', blank=True)
    pass_condition = models.IntegerField()
    passed = models.ManyToManyField(UserInfo, related_name='passed', blank=True)

    def __str__(self):
        return (str(self.day) + ' 챌린지, since ' + str(self.start_date))
