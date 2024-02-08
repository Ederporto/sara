from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.filter
def categorize(a, b):
    try:
        return min(int(a/(0.25*b)) + 1, 5)
    except:
        return "-"


@register.filter
def perc(a, b):
    try:
        return "{:.0f}%".format(100*a/b, 1)
    except:
        return "-"


@register.filter
def bool_yesno(a):
    if type(a) == bool:
        return _("Yes") if a else _("No")
    else:
        return a


@register.filter
def is_yesno(a):
    if type(a) == bool:
        return True
    else:
        return False