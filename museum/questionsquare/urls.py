from django.urls import path
from . import views

urlpatterns = [
    path('', views.question_square, name="question-square"),
    path('throw-question', views.create_ques_from_others, name="create-ques-from-others"),
    path('edit-question/<int:ques_others_id>', views.update_ques_from_others, name="update-ques-from-others"),
    path('delete-question/<int:ques_others_id>', views.delete_ques_from_others, name="delete-ques-from-others"),
    
    path('answers-of/<int:ques_id>', views.view_ans_others, name="view-ans-others"),
    path('answer-to/<int:ques_others_id>', views.create_ans_others, name="create-ans-others"),
    path('answer/<int:ans_others_id>', views.detail_ans_others, name="detail-ans-others"),
    path('edit-answer/<int:ans_others_id>', views.update_ans_others, name="update-ans-others"),
    path('delete-answer/<int:ans_others_id>', views.delete_ans_others, name="delete-ans-others"),
] 