from django.db import models
from django.contrib.auth.models import User
from member.models import UserInfo
# Create your models here.

class QuestionsFromOthers(models.Model):
    objects = models.Manager()
    questioner = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name='questionfromothers', default=None)
    title = models.CharField(max_length=100, blank=False)
    desc = models.TextField(blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='question_img')
    created_at = models.DateField(auto_now_add=True)
    created_at_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (str(self.title) + ' by : ' + str(self.questioner))

class AnswersForFromOthers(models.Model):
    objects = models.Manager()
    question_id = models.ForeignKey(QuestionsFromOthers, on_delete=models.CASCADE, related_name='answersforfromothers', default=None)
    author = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name='answersforfromothers', default=None)
    body = models.CharField(max_length=10000, blank=False)
    image = models.ImageField(null=True, blank=True, upload_to='answer_img')
    created_at = models.DateField(auto_now_add=True)
    created_at_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (str(self.question_id) + ', ' + str(self.author))