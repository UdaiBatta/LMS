from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Template filter to look up dictionary values by key"""
    if dictionary and hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None

@register.filter
def get_item(dictionary, key):
    """Alternative template filter to get dictionary items"""
    return dictionary.get(key) if dictionary else None
