from dataclasses import dataclass, field

from django.db import models

from common.api.api_resources import (
    ApiResource,
    ApiResourceUtilsMixin,
    InnerApiResource,
)


@dataclass(frozen=True)
class User(ApiResourceUtilsMixin, InnerApiResource):
    class Type(models.TextChoices):
        PRO = "pro", "プロユーザ"
        ADMIN = "admin", "管理者"
        CONTRACTOR = "contractor", "法人契約者"

    name: str = field(init=False)
    type: Type = field(init=False)

    def __post_init__(self):
        self._init_attr("name", self._inner_response_data["name"])
        self._init_attr("type", self.Type(self._inner_response_data["child_type"]))


@dataclass(frozen=True)
class Session(ApiResourceUtilsMixin, ApiResource):
    # NOTE: None の場合未認証のため、認証済みか判定する場合は `if session.user:` で判定する
    user: User | None = field(init=False)
    csrf_token: str = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        res = self._api_result.response_data
        self._init_attr("user", User(res["user"]) if res["user"] else None)
        self._init_attr("csrf_token", res["csrf_token"])
