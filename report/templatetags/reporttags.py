from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.filter
def get_attribute(instance, *field_names):
    try:
        for field_name in field_names:
            field_value = getattr(instance, field_name)
            if field_value is not None and field_value:
                return True
        return False
    except AttributeError:
        return False
