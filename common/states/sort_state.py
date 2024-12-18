import dataclasses

from django.http import HttpRequest, QueryDict


@dataclasses.dataclass(frozen=True)
class SortState:
    """リストのソート状態を管理する Value Object

    View でインスタンス化し、context に渡して Template で用いる。その際に Template で必要なソートに関するロジックをこのクラスに記述する。
    """

    DESC_SIGN = "-"

    request: HttpRequest

    def render_href(self, sort_key: str) -> str:
        current_query_dict: QueryDict = self.request.GET.copy()

        if self.is_sorting_by(sort_key):
            # NOTE: すでに該当の sort_key でソートされている場合は、ソート順を逆にする
            current_query_dict["sort"] = sort_key if self.is_desc else f"{self.DESC_SIGN}{sort_key}"
        else:
            # NOTE: それ以外の場合は、初期状態の降順でソートする
            current_query_dict["sort"] = f"{self.DESC_SIGN}{sort_key}"

        # NOTE: ページネーションをリセットする
        current_query_dict.pop("page", None)

        return "?" + current_query_dict.urlencode()

    def is_sorting_by(self, sort_key: str) -> bool:
        return self._current_sort_key == sort_key

    @property
    def is_desc(self) -> bool:
        return self._current_sort_query.startswith(self.DESC_SIGN)

    @property
    def _current_sort_key(self) -> str:
        return self._current_sort_query[1:] if self.is_desc else self._current_sort_query

    @property
    def _current_sort_query(self) -> str:
        return self.request.GET.get("sort", "")
