from django.urls import path

from materials.apps import MaterialsConfig
from materials.views import home, SubjectListView, SubjectDetailView, \
    SubjectCreateView, SubjectUpdateView, SubjectDeleteView, \
    set_published_theme, MyThemeListView, ThemeCreateView, ThemeDetailView, \
    ThemeUpdateView, ThemeDeleteView, LessonDetailView, set_published_lesson, \
    LessonCreateView, MyLessonListView, LessonUpdateView, LessonDeleteView, \
    TestingCreateView, MyTestsView, TestListView, TestDetailView, \
    TestUpdateView, TestDeleteView, set_published_test, TestPassView, \
    QuestionCreateView, QuestionUpdateView, ResultDeleteView, \
    ResultCreateView, ResultListView, QuestionDeleteView

app_name = MaterialsConfig.name

urlpatterns = [
    path('', home, name='home'),  # домашняя страница (корневой url)
    # Subject urls
    path('subjects/', SubjectListView.as_view(), name='subjects'),
    path('subjects/<int:pk>', SubjectDetailView.as_view(),
         name='subject_detail'),
    path('subjects/create/', SubjectCreateView.as_view(),
         name='subject_create'),
    path('subjects/update/<int:pk>', SubjectUpdateView.as_view(),
         name='subject_update'),
    path('subjects/delete/<int:pk>', SubjectDeleteView.as_view(),
         name='subject_delete'),
    # Theme urls
    path('themes/set-published/<int:pk>', set_published_theme,
         name='set_published_theme'),
    path('my-themes/', MyThemeListView.as_view(), name='my_themes'),
    path('themes/create/', ThemeCreateView.as_view(), name='themes_create'),
    path('themes/<int:pk>', ThemeDetailView.as_view(), name='theme_detail'),
    path('themes/update/<int:pk>', ThemeUpdateView.as_view(),
         name='theme_update'),
    path('themes/delete/<int:pk>', ThemeDeleteView.as_view(),
         name='theme_delete'),
    # Lesson urls
    path('lessons/<int:pk>', LessonDetailView.as_view(), name='lesson_detail'),
    path('lessons/set-published/<int:pk>', set_published_lesson,
         name='set_published_lesson'),
    path('lessons/create/', LessonCreateView.as_view(), name='lesson_create'),
    path('my-lessons/', MyLessonListView.as_view(), name='my_lessons'),
    path('lessons/update/<int:pk>', LessonUpdateView.as_view(),
         name='lesson_update'),
    path('lessons/delete/<int:pk>', LessonDeleteView.as_view(),
         name='lesson_delete'),
    # Test urls
    path('test/create/', TestingCreateView.as_view(), name='test_create'),
    path('my-tests/', MyTestsView.as_view(), name='my_tests'),
    path('test/list/<int:pk>', TestListView.as_view(), name='test_list'),
    path('test/<int:pk>', TestDetailView.as_view(), name='test_detail'),
    path('test/update/<int:pk>', TestUpdateView.as_view(), name='test_update'),
    path('test/delete/<int:pk>', TestDeleteView.as_view(), name='test_delete'),
    path('test/set-published/<int:pk>', set_published_test,
         name='test_set_published'),
    path('test/pass/<int:pk>', TestPassView.as_view(), name='test_passing'),
    # Question urls
    path('questions/create/<int:pk>', QuestionCreateView.as_view(),
         name='question_create'),
    path('questions/update/<int:pk>', QuestionUpdateView.as_view(),
         name='question_update'),
    path('questions/delete/<int:pk>', QuestionDeleteView.as_view(),
         name='question_delete'),
    # Result urls
    path('result/<int:pk>', ResultCreateView.as_view(), name='result_new'),
    path('result/', ResultListView.as_view(), name='my_result'),
    path('result/delete/<int:pk>', ResultDeleteView.as_view(),
         name='result_delete'),
]
