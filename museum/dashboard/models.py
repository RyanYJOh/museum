from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from member.models import UserInfo
from main.models import AnswersForFromUs, AnswersForFromSelf

# Create your models here.
class Clicks(models.Model):
    USER_TYPE = (
        ('Adam','Adam'),
        ('Brian','Brian'),
        ('Claire','Claire'),
        ('Diana','Diana')
    )

    ANS_TYPE = (
        ('us','us'),
        ('self','self'),
    )

    objects = models.Manager()

    clicked_from = models.CharField(max_length=20, null=True, blank=True)
    whose_post = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clicks', null=True, default=None )
    ans_type = models.CharField(max_length=10, choices=ANS_TYPE)
    ans_us_ref = models.ForeignKey(AnswersForFromUs, on_delete=models.CASCADE, related_name='clicks', null=True)
    ans_self_ref = models.ForeignKey(AnswersForFromSelf, on_delete=models.CASCADE, related_name='clicks', null=True)
    clicked_at = models.DateField(auto_now_add=True)
    clicked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clicked_by', null=True, default=None)
    clicked_user_type = models.CharField(max_length=20, choices=USER_TYPE)

    def __str__(self):
        return ('Viewed by ' + str(self.clicked_user_type) + ' from [' + str(self.clicked_from) + ']')