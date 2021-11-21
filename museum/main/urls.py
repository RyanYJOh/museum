from django.urls import path
from . import views
from dashboard.views import clicks
from register import views as registerViews

urlpatterns = [
    path('', views.main_page, name='home'),
    path('filter=<int:question_no>', views.main_page_filtered, name="home-filtered"),
    # path('me', views.my_profile, name='my-profile'),
    path('profile/<str:username>', views.profile, name='others-profile'),
    path('about', views.about, name="about"),
    path('getThisAns/<str:ques_from>/<int:id>', views.detail_modal, name='others-profile'),

    ## Us
    path('question-from-originals', views.create_ans_us_short, name='question-from-originals'),
    path('originals-answer/<int:ans_us_id>', views.detail_ans_us, name='originals-answer-detail'),
    path('originals-answer/edit/<int:ans_us_id>', views.update_ans_us, name="update-answer-from-originals"),
    path('originals-answer/delete/<int:ans_us_id>', views.delete_ans_us, name="delete-answer-from-originals"),
    
    ## Self
    path('question-from-myself', views.create_ans_self, name="question-from-myself"),
    path('self-answer/<int:ans_self_id>', views.detail_ans_self, name="answer-from-myself"),
    path('self-answer/edit/<int:ans_self_id>', views.update_ans_self, name="update-answer-from-myself"),
    path('self-answer/delete/<int:ans_self_id>', views.delete_ans_self, name="delete-answer-from-myself"),

    ## Bookmark, Non-member answer
    path('ajax/bookmark', views.bookmark, name="bookmark"),
    path('ajax/author-favorite', views.author_favorite, name="author-favorite"),
    path('ajax/non-member-answer', registerViews.nonMemberAnswer, name="non-member-answer"),
    path('ajax/clicks', clicks, name="clicks"),

    ## Comments
    # Create
    path('ajax/create-comment-ans-us', views.create_comment_ans_us, name="create_comment_ans_us"),
    path('ajax/create-comment-ans-self', views.create_comment_ans_self, name="create_comment_ans_self"),
    # Delete
    path('ajax/del-comment-ans-us', views.del_comment_ans_us, name="delete-comment-ans-us"),
    path('ajax/del-comment-ans-self', views.del_comment_ans_self, name="delete-comment-ans-self"),
] 