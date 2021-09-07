from django.db import models
from django.contrib.auth.models import User
# Create your models here.

'''
class Questions(models.Model):
    TYPE_CHOICES = (
        ('from_museum' , '뮤지엄이 던지는'),
        ('from_self', '내가 나에게 던지는'),
        ('from_others', '다른 이에게 던지는')
    )

    objects = models.Manager()
    title = models.CharField(max_length = 100, blank=False)
    body = models.TextField(blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="question_img")
    from_type = models.CharField(max_length=50, choices=TYPE_CHOICES, null=False) # 여기서 null=False는 선택하지 않을 수는 없다는 거겠지?
    is_nudge = models.BooleanField(default=False)
    createdAt = models.DateField(auto_now_add=True)

class Answers(models.Model):
    objects = models.Manager()

    question_id = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='answer', null=False) # default 필요한가?
    self_question_title = models.CharField(max_length=100, blank=False) # 여기에 값이 있는 경우, 이 타이틀이 Questions에도 저장된다.
    self_answer_subtitle = models.CharField(max_length=100, blank=True)
    body = models.CharField(max_length=10000, blank=True) # 답변을 하지 않고 저장하는 경우--null=True 필요없나?
'''
class QuestionsFromUs(models.Model):
    objects = models.Manager()
    question_no = models.IntegerField(null=True)
    title = models.CharField(max_length = 100, blank=False)
    body = models.TextField(blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="question_img")
    is_nudge = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

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
    created_at = models.DateField(auto_now_add=False)
    updated_at = models.DateField(auto_now_add=True)
    created_at_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_shared = models.BooleanField(default=True)
    on_magazine = models.BooleanField(default=False)

    def __str__(self):
        return (str(self.author_id)+'__'+str(self.question_id)+'__'+str(self.created_at))

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
    updated_at = models.DateField(auto_now_add=False)
    created_at_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_shared = models.BooleanField(default=True)
    on_magazine = models.BooleanField(default=False)

    def __str__(self):
        return (str(self.author_id) + '--' + str(self.question_id))

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
        return str(self.bookmarker) + '--' + str(self.ans_type) + '--' + str(self.ans_us_ref) + ' or ' + str(self.ans_self_ref)

class RandomImages(models.Model):
    objects = models.Manager()
    color_name = models.CharField(max_length=10, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='random_images')

    def __str__(self):
        return str(self.color_name)