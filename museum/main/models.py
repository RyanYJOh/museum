from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.

class QuestionsFromUs(models.Model):
    objects = models.Manager()
    question_no = models.IntegerField(null=True)
    title = models.CharField(max_length = 100, blank=False)
    body = models.TextField(blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="question_img")
    is_nudge = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return (str(self.question_no) + '. ' + str(self.title))

class QuestionsFromSelf(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length = 100, blank=False)
    question_no = models.IntegerField(null=True, unique=True) ## Reference용이 아닌, [질문 번호] 그 자체를 가져올 때만 사용
    image = models.ImageField(null=True, blank=True, upload_to="question_img")
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

# class QuestionsFromOthers(models.Model):

class AnswersForFromUs(models.Model):
    objects = models.Manager()
    type = models.CharField(max_length=10, default='us', blank=True)
    # answer_no = models.IntegerField(null=True, unique=True) ## Reference용이 아닌, [정답 번호] 그 자체를 가져올 때만 사용
    question_id = models.ForeignKey(QuestionsFromUs, on_delete=models.CASCADE, related_name='answerforfromus', null=False, default=None)
    author_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answerforfromus', null=False)
    body = models.CharField(max_length=10000, blank=True) # 답변을 하지 않고 저장하는 경우--null=True 필요없나?
    image = models.ImageField(null=True, blank=True, upload_to='answer_img')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)
    created_at_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_shared = models.BooleanField(default=True)
    on_magazine = models.BooleanField(default=False)
    author_favorite = models.BooleanField(default=False)
    from_today_ques = models.BooleanField(default=True)

    def __str__(self):
        # return (str(self.question_id.question_no) + ' answered by: ' + str(self.author_id) + ', on '+str(self.created_at))
        return (str(self.question_id) + ' answered by: ' + str(self.author_id) + ', on '+str(self.created_at))

class AnswersForFromSelf(models.Model):
    objects = models.Manager()
    type = models.CharField(max_length=10, default='self', blank=True)
    # answer_no = models.IntegerField(null=True, unique=True) ## Reference용이 아닌, [정답 번호] 그 자체를 가져올 때만 사용
    question_id = models.ForeignKey(QuestionsFromSelf, on_delete=models.CASCADE, related_name='answerforfromself', null=False, default=None)
    author_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answerforfromself', null=False)
    subtitle = models.CharField(max_length=100, blank=True)
    body = models.CharField(max_length=10000, blank=True) # 답변을 하지 않고 저장하는 경우--null=True 필요없나?
    image = models.ImageField(null=True, blank=True, upload_to='answer_img')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)
    created_at_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_shared = models.BooleanField(default=True)
    on_magazine = models.BooleanField(default=False)
    author_favorite = models.BooleanField(default=False)

    def __str__(self):
        return (str(self.author_id) + ' wrote about: ' + str(self.question_id))

# class AnswersForFromOthers(models.Model):

class SavedAnswers(models.Model):
    ANS_TYPE = (
        ('us','us'),
        ('self','self'),
    )

    objects = models.Manager()
    bookmarker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savedanswers', null=True, default=None)
    ans_type = models.CharField(max_length=10, choices=ANS_TYPE)
    ans_us_ref = models.ForeignKey(AnswersForFromUs, on_delete=models.CASCADE, related_name='savedanswers', null=True)
    ans_self_ref = models.ForeignKey(AnswersForFromSelf, on_delete=models.CASCADE, related_name='savedanswers', null=True)

    def __str__(self):
        return (str(self.bookmarker) + ' saved: ' + '"' + str(self.ans_type) + '", ' + str(self.ans_us_ref) + ' or ' + str(self.ans_self_ref))

class RandomImages(models.Model):
    objects = models.Manager()
    color_name = models.CharField(max_length=10, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='random_images')

    def __str__(self):
        return str(self.color_name)

class CommentAnsUs(models.Model):
    objects = models.Manager()
    ans = models.ForeignKey(AnswersForFromUs, on_delete=models.CASCADE, related_name='commentansus', null=True, default=None)
    created_at_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    author = models.ForeignKey('member.UserInfo', on_delete=models.CASCADE, related_name='commentusauthor', null=True, default=None)
    body = models.CharField(max_length=2000, null=True, blank=True)

    def __str__(self):
        return str(self.author)+', '+str(self.created_at_time)

class CommentAnsSelf(models.Model):
    objects = models.Manager()
    ans = models.ForeignKey(AnswersForFromSelf, on_delete=models.CASCADE, related_name='commentansself', null=True, default=None)
    created_at_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    author = models.ForeignKey('member.UserInfo', on_delete=models.CASCADE, related_name='commentselfauthor', null=True, default=None)
    body = models.CharField(max_length=2000, null=True, blank=True)

    def __str__(self):
        return str(self.author)+', '+str(self.created_at_time)

class Likes(models.Model):
    ANS_TYPE = (
        ('us','us'),
        ('self','self'),
    )

    objects = models.Manager()
    liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', null=True, default=None)
    ans_type = models.CharField(max_length=10, choices=ANS_TYPE)
    ans_us_ref = models.ForeignKey(AnswersForFromUs, on_delete=models.CASCADE, related_name='likesUs', null=True)
    ans_self_ref = models.ForeignKey(AnswersForFromSelf, on_delete=models.CASCADE, related_name='likesSelf', null=True)

    def __str__(self):
        return (str(self.liker) + ' liked: ' + '"' + str(self.ans_type) + '", ' + str(self.ans_us_ref) + ' or ' + str(self.ans_self_ref))

class Notice(models.Model):
    objects = models.Manager()
    label = models.CharField(max_length=10, blank=True)
    title = models.CharField(max_length=100, blank=False)
    body = models.TextField(blank=False)
    image = models.ImageField(null=True, blank=True, upload_to='notice_img')
    created_at = models.DateField(auto_now_add=False)

    def __str__(self):
        return ('['+str(self.created_at)+'] '+str(self.title))

class CrysRegistration(models.Model):
    objects = models.Manager()
    email = models.EmailField()
    name = models.CharField(max_length=100, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return (str(self.email) + '(' + str(self.name) + ')')