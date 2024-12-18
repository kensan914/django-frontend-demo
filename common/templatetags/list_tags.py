from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag(takes_context=True)
def sort_header(context, sort_key: str, label: str):
    if (sort_state := context.get("sort_state")) is None:
        raise ValueError("sort_state is required in context")

    if sort_state.is_sorting_by(sort_key):
        sort_sign = "▼" if sort_state.is_desc else "▲"
    else:
        sort_sign = ""

    return format_html(
        '<a href="{href}">{children}</a>',
        href=sort_state.render_href(sort_key),
        children=f"{label}{sort_sign}",
    )
