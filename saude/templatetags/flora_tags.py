from datetime import date, datetime
from django import template
from django.db.models.fields.files import FieldFile

register = template.Library()


@register.filter
def get_attr(obj, attr):
    display = getattr(obj, f"get_{attr}_display", None)

    if callable(display):
        return display()

    value = getattr(obj, attr, None)

    if callable(value):
        value = value()

    if value is True:
        return "Sim"

    if value is False:
        return "Não"

    if value in (None, ""):
        return "—"

    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y às %H:%M")

    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")

    if isinstance(value, FieldFile):
        return value.name or "—"

    return value


@register.filter
def widget_type(field):
    return field.field.widget.__class__.__name__.lower()