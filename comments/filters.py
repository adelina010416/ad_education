import django_filters

from comments.models import Comment


class CommentFilter(django_filters.FilterSet):
    """Фильтр комментариев"""
    text = django_filters.CharFilter(lookup_expr='icontains')
    theme__title = django_filters.CharFilter(lookup_expr='icontains')
    lesson__title = django_filters.CharFilter(lookup_expr='icontains')
    test__title = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Comment
        fields = ['text', 'theme', 'lesson']
