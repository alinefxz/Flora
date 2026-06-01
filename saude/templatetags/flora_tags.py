from django import template

register = template.Library()


@register.filter
def get_attr(obj, attr):
    value = obj

    for part in attr.split("."):
        value = getattr(value, part, "")

    if callable(value):
        value = value()

    if value is True:
        return "Sim"

    if value is False:
        return "Não"

    if value is None:
        return "-"

    return value