from django.urls import path
from . import views
from register import views as registerViews

urlpatterns = [
    path('', views.main_page, name='home'),
    # path('me', views.my_profile, name='my-profile'),
    path('profile/<str:username>', views.profile, name='others-profile'),
    path('what-is-originals', views.about, name="about"),

    ## Us
    path('question-from-originals', views.create_ans_us_short, name='question-from-originals'),
    path('answer-long', views.create_ans_us_long, name='answer-long'),
    path('originals-answer/<int:ans_us_id>', views.detail_ans_us, name='originals-answer-detail'),
    path('originals-answer/edit/<int:ans_us_id>', views.update_ans_us, name="update-answer-from-originals"),
    
    ## Self
    path('question-from-myself', views.create_ans_self, name="question-from-myself"),
    path('self-answer/<int:ans_self_id>', views.detail_ans_self, name="answer-from-myself"),
    path('self-answer/edit/<int:ans_self_id>', views.update_ans_self, name="update-answer-from-myself"),

    ## Bookmark, Non-member answer
    path('ajax/bookmark', views.bookmark, name="bookmark"),
    path('ajax/non-member-answer', registerViews.nonMemberAnswer, name="non-member-answer")
]