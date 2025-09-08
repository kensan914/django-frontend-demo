from urllib.parse import urljoin

import requests
import responses

from common.api import api_settings
from common.api.api_results import ApiResult
from config import settings


class ApiClient:
    """API クライアント

    # エンドポイントメソッドのコーディング規約
    - requests は直接用いず、self.requests_session を用いる（セッションID/CSRFトークンのクッキー管理や、キープアライブによるパフォーマス向上の目的）
        - FYI: https://requests.readthedocs.io/en/latest/user/advanced/#session-objects
    - URL の生成は、 self.url() メソッドを用いる
    - ApiResult インスタンスを返す
    - メソッド名の命名規則: `{HTTPメソッド名}_{リソース名やパスが推測できる名前}`
    - timeout=self.TIMEOUT を指定する

    Example:
    def post_users(self, name: str, age: int) -> ApiResult:
        response = self.requests_session.post(
            self.url(path="/users/"),
            data={"name": name, "age": age},
            timeout=self.TIMEOUT,
        )
        return ApiResult(response)
    """

    TIMEOUT = 10  # seconds

    def __init__(self) -> None:
        # NOTE: API のセッションと区別するため、`requests_` プレフィックスを付与
        self.requests_session = requests.Session()

    def url(self, path: str) -> str:
        """パスを受け取り、API の絶対 URL を返す"""
        if not (base_url := settings.env("API_BASE_URL")):
            raise ValueError("環境変数 API_BASE_URL が設定されていません")

        # NOTE: API（Django）の動作として、末尾スラッシュなしの場合に末尾スラッシュありの URL にリダイレクトされるため、この時点で末尾スラッシュを付与する
        path_with_trailing_slash = path if path.endswith("/") else (path + "/")
        return urljoin(base_url, path_with_trailing_slash)

    def set_session_id(self, session_id: str) -> None:
        """ログイン時に発行されたセッション ID を API クライアントのクッキーにセットする
        認証を必要とする API リクエストを行う前に呼び出す必要がある
        """
        self.requests_session.cookies.set(api_settings.SESSION_COOKIE_NAME, session_id)

    def set_csrf_token(self, api_csrf_token: str) -> None:
        """フロントサーバ側の CSRF トークンではなく、API 側の CSRF トークンを別途取得して HTTP ヘッダにセットする
        CSRF 検証を必要とする API リクエストを行う前に呼び出す必要がある
        FYI: CSRF 検証を必要とする API？ -> 認証が必要でかつ POST/PUT/PATCH/DELETE のいずれかのメソッド (https://www.django-rest-framework.org/topics/ajax-csrf-cors/#csrf-protection )
        """
        self.requests_session.headers.update(
            {api_settings.CSRF_HEADER_NAME: api_csrf_token}
        )

    def get_session_and_set_csrf_cookie(self) -> ApiResult:
        """API からセッション情報（ログインユーザ情報やCSRFトークン/CSRFクッキー）を取得し、CSRF クッキーを API クライアントのクッキーにセットする
        CSRF 検証を必要とする API リクエストを行う前に呼び出す必要がある
        FYI: CSRF 検証を必要とする API？ -> 認証が必要でかつ POST/PUT/PATCH/DELETE のいずれかのメソッド (https://www.django-rest-framework.org/topics/ajax-csrf-cors/#csrf-protection )
        """
        # NOTE: /session/ API リクエストで、CSRF クッキーが self.requests_session に Set-Cookie される
        #       /session/ API レスポンスに含まれる CSRF トークンとは別物 https://docs.djangoproject.com/ja/4.2/howto/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false
        response = self.requests_session.get(
            self.url(path="/session/"),
            timeout=self.TIMEOUT,
        )
        return ApiResult(response)

    def post_login(self, email: str, password: str) -> ApiResult:
        response = self.requests_session.post(
            self.url(path="/login/"),
            data={"email": email, "password": password},
            timeout=self.TIMEOUT,
        )
        return ApiResult(response)

    def post_logout(self) -> ApiResult:
        response = self.requests_session.post(
            self.url(path="/logout/"),
            timeout=self.TIMEOUT,
        )
        return ApiResult(response)

    @responses.activate  # WARNING: モック
    def get_mails(
        self,
        q: "str | None",
        sort: "str | None",
        page: "str | None",
    ) -> ApiResult:
        # WARNING: モック
        responses.get(
            self.url(path="/mails/"),
            status=200,
            json={
                "mails": [
                    {
                        "id": "1",
                        "type": "メールA",
                        "title": "タイトル1",
                        "sent_at": "2021/01/01",
                    },
                    {
                        "id": "2",
                        "type": "メールA",
                        "title": "タイトル2",
                        "sent_at": "2021/01/02",
                    },
                    {
                        "id": "3",
                        "type": "メールC",
                        "title": "タイトル3",
                        "sent_at": "2021/01/03",
                    },
                    {
                        "id": "4",
                        "type": "メールB",
                        "title": "タイトル4",
                        "sent_at": "2021/01/04",
                    },
                    {
                        "id": "5",
                        "type": "メールA",
                        "title": "タイトル5",
                        "sent_at": "2021/01/05",
                    },
                    {
                        "id": "6",
                        "type": "メールB",
                        "title": "タイトル6",
                        "sent_at": "2021/01/06",
                    },
                    {
                        "id": "7",
                        "type": "メールA",
                        "title": "タイトル7",
                        "sent_at": "2021/01/07",
                    },
                ],
                "pagination": {
                    "current_page": int(page or 1),
                    "total_pages": 3,
                },
            },
        )
        # responses.get(
        #     self.url(path="/mails/"),
        #     status=403,
        #     json={"error": {"message": "権限がありません"}},
        # )
        # responses.get(
        #     self.url(path="/mails/"),
        #     status=500,
        #     json={"error": {"message": "処理が失敗しました"}},
        # )

        params = {}
        if q is not None:
            params["q"] = q
        if sort is not None:
            params["sort"] = sort
        if page is not None:
            params["page"] = page
        response = self.requests_session.get(
            self.url(path="/mails/"),
            params=params,
            timeout=self.TIMEOUT,
        )
        return ApiResult(response)

    @responses.activate  # WARNING: モック
    def get_mail_detail(self, mail_id: int) -> ApiResult:
        # WARNING: モック
        responses.get(
            self.url(path="/mails/1/"),
            status=200,
            json={
                "mail": {
                    "id": "1",
                    "type": "メールA---",
                    "title": "タイトル1",
                    "sent_at": "2021/01/01",
                },
            },
        )
        # responses.get(
        #     self.url(path=f"/mails/1/"),
        #     status=403,
        #     json={"error": {"message": "権限がありません"}},
        # )
        # responses.get(
        #     self.url(path=f"/mails/1/"),
        #     status=404,
        #     json={"error": {"message": "メールが見つかりませんでした"}},
        # )
        # responses.get(
        #     self.url(path=f"/mails/1/"),
        #     status=500,
        #     json={"error": {"message": "処理が失敗しました"}},
        # )

        response = self.requests_session.get(
            self.url(path=f"/mails/{mail_id}/"),
            timeout=self.TIMEOUT,
        )
        return ApiResult(response)

    @responses.activate  # WARNING: モック
    def post_mail(self, type_: str, title: str, text: str) -> ApiResult:
        # WARNING: モック
        # responses.post(
        #     self.url(path="/mails/"),
        #     status=200,
        #     json={"mail": {"id": "1", "type": "メールA", "title": "タイトル1", "sent_at": "2021/01/01"}},
        # )
        responses.post(
            self.url(path="/mails/"),
            status=400,
            json={
                "validation": True,
                "errors": {
                    "non_field_error": [
                        "フィールド以外のエラーメッセージです1",
                        "フィールド以外のエラーメッセージです2",
                    ],
                    "type": [
                        "メール種別のエラーメッセージです1",
                        "メール種別のエラーメッセージです2",
                    ],
                    "title": [
                        "メール件名のエラーメッセージです1",
                        "メール件名のエラーメッセージです2",
                    ],
                    "text": ["メール本文のエラーメッセージです"],
                },
            },
        )

        response = self.requests_session.post(
            self.url(path="/mails/"),
            data={"type": type_, "title": title, "text": text},
            timeout=self.TIMEOUT,
        )
        return ApiResult(response)

    def get_pro_users(self) -> ApiResult:
        response = self.requests_session.get(
            self.url(path="/pro-users/"),
            timeout=self.TIMEOUT,
        )
        return ApiResult(response)

    def get_admin_users(self) -> ApiResult:
        response = self.requests_session.get(
            self.url(path="/admin-users/"),
            timeout=self.TIMEOUT,
        )
        return ApiResult(response)

    def get_contractors(self) -> ApiResult:
        response = self.requests_session.get(
            self.url(path="/contractors/"),
            timeout=self.TIMEOUT,
        )
        return ApiResult(response)
