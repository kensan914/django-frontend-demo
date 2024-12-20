from django_components import Component, register

from common.states.pagination_state import PaginationState


@register("pagination")
class Pagination(Component):
    template_name = "pagination/template.html"

    def get_context_data(self, pagination_state: PaginationState):
        return {
            "pagination_state": pagination_state,
        }
