import dataclasses
from functools import cached_property
from http.cookiejar import Cookie

import requests

from common.api import api_settings
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
    def is_401(self) -> bool:
        return self.response.status_code == requests.codes.unauthorized

    @property
    def is_403(self) -> bool:
        return self.response.status_code == requests.codes.forbidden

    @property
    def is_404(self) -> bool:
        return self.response.status_code == requests.codes.not_found

    def get_session_cookie_params(self) -> dict | None:
        """Django の HttpResponse の set_cookie メソッドに渡すための Cookie パラメータを取得する"""

        session_cookie: Cookie | None = None
        for domain, domain_cookies in self.response.cookies._cookies.items():
            for path, path_cookies in domain_cookies.items():
                if api_settings.SESSION_COOKIE_NAME in path_cookies:
                    session_cookie = path_cookies[api_settings.SESSION_COOKIE_NAME]
                    break
            # NOTE: 上記 break で、2つの多重ループを抜け出す
            else:
                continue
            break
        if session_cookie is None:
            return None

        return {
            "value": session_cookie.value,
            "max_age": None,  # TODO
            "expires": session_cookie.expires,
            "path": session_cookie.path,
            # NOTE: session_cookie には API のドメインが保持されているため
            "domain": None,
            "secure": session_cookie.secure,
            "httponly": session_cookie._rest.get("HttpOnly", False),
            "samesite": session_cookie._rest.get("SameSite", "Lax"),
        }
