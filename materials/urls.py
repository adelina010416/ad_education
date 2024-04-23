from django.urls import path

from materials.apps import MaterialsConfig
from materials.views import *

app_name = MaterialsConfig.name

urlpatterns = [
    path('', home, name='home'),

    path('subjects/', SubjectListView.as_view(), name='subjects'),
    path('subjects/<int:pk>', SubjectDetailView.as_view(), name='subject_detail'),
    path('subjects/create/', SubjectCreateView.as_view(), name='subject_create'),
    path('subjects/update/<int:pk>', SubjectUpdateView.as_view(), name='subject_update'),
    path('subjects/delete/<int:pk>', SubjectDeleteView.as_view(), name='subject_delete'),

    path('themes/set-published/<int:pk>', set_published_theme, name='set_published_theme'),
    path('my-themes/', MyThemeListView.as_view(), name='my_themes'),
    path('themes/create/', ThemeCreateView.as_view(), name='themes_create'),
    path('themes/<int:pk>', ThemeDetailView.as_view(), name='theme_detail'),
    path('themes/update/<int:pk>', ThemeUpdateView.as_view(), name='theme_update'),
    path('themes/delete/<int:pk>', ThemeDeleteView.as_view(), name='theme_delete'),

    path('lessons/<int:pk>', LessonDetailView.as_view(), name='lesson_detail'),
    path('lessons/set-published/<int:pk>', set_published_lesson, name='set_published_lesson'),
    path('lessons/create/', LessonCreateView.as_view(), name='lesson_create'),
    path('my-lessons/', MyLessonListView.as_view(), name='my_lessons'),
    path('lessons/update/<int:pk>', LessonUpdateView.as_view(), name='lesson_update'),
    path('lessons/delete/<int:pk>', LessonDeleteView.as_view(), name='lesson_delete'),

    path('comments/<int:pk>', ThemeCommentView.as_view(), name='theme_comments'),
    path('my-comments/', MyCommentListView.as_view(), name='my_comments'),
    path('comments/update/<int:pk>', CommentUpdateView.as_view(), name='comments_update'),
    path('comments/delete/<int:pk>', CommentDeleteView.as_view(), name='comments_delete'),
]
