from django.template import Library

register = Library()

@register.filter(name='split_movieId_title')
def split_movieId_title(value):
    return " ".join(value.split('_')[1:])