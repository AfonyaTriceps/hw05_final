from django import template
from django.forms.boundfield import BoundField
from django.utils.safestring import SafeText

register = template.Library()


@register.filter
def addclass(field: BoundField, css: SafeText) -> SafeText:
    return field.as_widget(
        attrs={
            'class': css,
        },
    )
