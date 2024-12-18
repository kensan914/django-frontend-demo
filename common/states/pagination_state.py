import dataclasses

from django.http import HttpRequest, QueryDict


@dataclasses.dataclass(frozen=True)
class PaginationState:
    """リストのページネーション状態を管理する Value Object

    View でインスタンス化し、context に渡して Template で用いる。その際に Template で必要なページネーションに関するロジックをこのクラスに記述する。
    """

    pagination_response: dict
    request: HttpRequest

    @property
    def current_page(self) -> int:
        return self.pagination_response["current_page"]

    @property
    def total_pages(self) -> int:
        return self.pagination_response["total_pages"]

    @property
    def has_previous(self) -> bool:
        return self.current_page > 1

    @property
    def has_next(self) -> bool:
        return self.current_page < self.total_pages

    @property
    def previous_page_href(self) -> str:
        return self._render_page_href(page=self.current_page - 1)

    @property
    def next_page_href(self) -> str:
        return self._render_page_href(page=self.current_page + 1)

    @property
    def first_page_href(self) -> str:
        return self._render_page_href(page=1)

    @property
    def last_page_href(self) -> str:
        return self._render_page_href(page=self.total_pages)

    def _render_page_href(self, page: int) -> str:
        current_query_dict: QueryDict = self.request.GET.copy()
        current_query_dict["page"] = page
        return "?" + current_query_dict.urlencode()
