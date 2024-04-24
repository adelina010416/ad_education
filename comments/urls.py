from django.urls import path

from comments.apps import CommentsConfig
from comments.views import ThemeCommentView, MyCommentListView, \
    CommentUpdateView, CommentDeleteView, TestCommentView

app_name = CommentsConfig.name

urlpatterns = [
    path('<int:pk>', ThemeCommentView.as_view(), name='theme_comments'),
    path('test/<int:pk>', TestCommentView.as_view(), name='test_comments'),
    path('my-comments/', MyCommentListView.as_view(), name='my_comments'),
    path('update/<int:pk>', CommentUpdateView.as_view(),
         name='comments_update'),
    path('delete/<int:pk>', CommentDeleteView.as_view(),
         name='comments_delete'),
]
