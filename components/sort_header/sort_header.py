from django_components import Component, register

from common.states.sort_state import SortState


@register("sort_header")
class SortHeader(Component):
    template_name = "sort_header/template.html"

    def get_context_data(self, key: str, label: str, sort_state: SortState):
        if sort_state.is_sorting_by(key):
            sort_sign = "▼" if sort_state.is_desc else "▲"
        else:
            sort_sign = ""

        return {
            "href": sort_state.render_href(key),
            "children": f"{label}{sort_sign}",
        }
