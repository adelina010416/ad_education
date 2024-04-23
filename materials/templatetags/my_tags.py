import os.path

from django import template

from config.settings import MEDIA_URL

register = template.Library()


@register.simple_tag()
def mediapath(val):
    if val:
        return os.path.join(MEDIA_URL, str(val))
    return os.path.join(MEDIA_URL, 'barbrady.jpg')
