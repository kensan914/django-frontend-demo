import dataclasses
from functools import cached_property

import requests

from common.api.api_errors import ApiErrorType, api_error_factory


@dataclasses.dataclass(frozen=True)
class ApiResult:
    """API のレスポンスを管理する Value Object

    View でハンドリング処理を行いやすくするための共通化メソッドを実装
    """

    response: requests.Response

    def __post_init__(self) -> None:
        is_2xx = 200 <= self.response.status_code < 300  # noqa: PLR2004
        # NOTE: requests.Response の ok プロパティは 1xx,3xx でも True 判定となるため、その場合は予期せぬ例外扱いとする
        if self.response.ok and not is_2xx:
            msg = f"unexpected error: {self.response.status_code}"
            raise Exception(msg)

    @cached_property
    def error(self) -> "ApiErrorType | None":
        if self.response.ok:
            return None

        return api_error_factory(self.response_data)

    @cached_property
    def response_data(self) -> dict:
        return self.response.json()

    @property
    def is_403(self) -> bool:
        return self.response.status_code == requests.codes.forbidden

    @property
    def is_404(self) -> bool:
        return self.response.status_code == requests.codes.not_found
