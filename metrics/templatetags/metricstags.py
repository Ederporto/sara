from django import template
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
