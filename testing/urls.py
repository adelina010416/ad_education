from django.urls import path

from testing.apps import TestingConfig
from testing.views import *

app_name = TestingConfig.name

urlpatterns = [
    path('create/', TestingCreateView.as_view(), name='test_create'),
    path('my-tests/', MyTestsView.as_view(), name='my_tests'),
    path('list/<int:pk>', TestListView.as_view(), name='test_list'),
    path('<int:pk>', TestDetailView.as_view(), name='test_detail'),
    path('update/<int:pk>', TestUpdateView.as_view(), name='test_update'),
    path('delete/<int:pk>', TestDeleteView.as_view(), name='test_delete'),
    path('set-published/<int:pk>', set_published_lesson, name='test_set_published'),
    path('pass/<int:pk>', TestPassView.as_view(), name='test_passing'),

    path('questions/create/<int:pk>', QuestionCreateView.as_view(), name='question_create'),
    path('questions/update/<int:pk>', QuestionUpdateView.as_view(), name='question_update'),
    path('questions/delete/<int:pk>', ResultDeleteView.as_view(), name='question_delete'),

    path('result/<int:pk>', ResultCreateView.as_view(), name='result_new'),
    path('result/', ResultListView.as_view(), name='my_result'),
    path('result/delete/<int:pk>', ResultDeleteView.as_view(), name='result_delete'),
    ]
