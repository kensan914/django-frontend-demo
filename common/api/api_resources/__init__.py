from abc import ABCMeta
from dataclasses import dataclass

from common.api.api_results import ApiResult


@dataclass(frozen=True)
class ApiResource(metaclass=ABCMeta):
    _api_result: ApiResult

    def __post_init__(self):
        if self._api_result.error:
            msg = "エラーレスポンスのApiResultでApiResourceを初期化することはできません"
            raise ValueError(msg)


@dataclass(frozen=True)
class InnerApiResource(metaclass=ABCMeta):
    _inner_response_data: dict


class ApiResourceUtilsMixin:
    def _init_attr(self, attr_name: str, value) -> None:
        object.__setattr__(self, attr_name, value)
