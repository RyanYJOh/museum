from django.db import models
from django.contrib.auth.models import User
from main.models import AnswersForFromSelf, AnswersForFromUs
from member.models import UserInfo

# Create your models here.
class Challenge(models.Model):
    objects = models.Manager()

    day = models.IntegerField()
    start_date = models.DateField(auto_now_add=False)
    end_date = models.DateField(auto_now_add=False)
    title = models.CharField(max_length=30, null=True, blank=True)
    desc = models.CharField(max_length=200, null=True, blank=True)
    participant = models.ManyToManyField(UserInfo, related_name='participant', null=True)
    pass_condition = models.IntegerField()
    passed = models.ManyToManyField(UserInfo, related_name='passed', null=True)

    def __str__(self):
        return (str(self.day) + ' 챌린지, since ' + str(self.start_date))
