from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import ForeignKey
from main.models import AnswersForFromUs
# Create your models here.

class UserInfo(models.Model):
    objects = models.Manager()
    this_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'userinfo', null=True, default=None) ## UserInfo가 생성될 때마다 user에게 link된다.
    real_name = models.CharField(max_length=20, blank=True, default="내 이름")
    profile_image = models.ImageField(null=True, upload_to="profile_images", default="default_psa.jpg")
    self_intro = models.CharField(max_length=140, blank=True, default="나에 대한 간단한 소개")
    slug = models.SlugField(max_length=100, allow_unicode=True, null=False, blank=False)
    persona_type = models.CharField(max_length=50, null=False)
    is_editor = models.BooleanField(default=False)
    saved_answers = models.ForeignKey(AnswersForFromUs, on_delete=models.CASCADE, related_name = 'userinfo', null=True, default=None)
    # saved_magazines = ForeignKey(, )

    def __str__(self):
        return (str(self.this_user) + ', ' + self.real_name)