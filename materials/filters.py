import django_filters

from materials.models import Comment, Theme


class CommentFilter(django_filters.FilterSet):
    text = django_filters.CharFilter(lookup_expr='icontains')
    theme__title = django_filters.CharFilter(lookup_expr='icontains')
    lesson__title = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Comment
        fields = ['text', 'theme', 'lesson']


class ThemeFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Theme
        fields = ['title']


class LessonFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Theme
        fields = ['title']
