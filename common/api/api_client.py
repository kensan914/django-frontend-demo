from urllib.parse import urljoin

import requests
import responses

from common.api.api_results import ApiResult
from config import settings


class ApiClient:
    """API クライアント

    各メソッドでは、requests を用いて API にリクエストし、その Response オブジェクトを用いて ApiResult をインスタンス化して返す
    """

    BASE_URL = settings.env("API_BASE_URL")

    @responses.activate  # WARNING: モック
    def get_mails(
        self,
        q: "str | None",
        sort: "str | None",
        page: "str | None",
    ) -> ApiResult:
        # WARNING: モック
        responses.get(
            f"{self.BASE_URL}/mails/",
            status=200,
            json={
                "mails": [
                    {"id": "1", "type": "メールA", "title": "タイトル1", "sent_at": "2021/01/01"},
                    {"id": "2", "type": "メールA", "title": "タイトル2", "sent_at": "2021/01/02"},
                    {"id": "3", "type": "メールC", "title": "タイトル3", "sent_at": "2021/01/03"},
                    {"id": "4", "type": "メールB", "title": "タイトル4", "sent_at": "2021/01/04"},
                    {"id": "5", "type": "メールA", "title": "タイトル5", "sent_at": "2021/01/05"},
                    {"id": "6", "type": "メールB", "title": "タイトル6", "sent_at": "2021/01/06"},
                    {"id": "7", "type": "メールA", "title": "タイトル7", "sent_at": "2021/01/07"},
                ],
                "pagination": {
                    "current_page": int(page or 1),
                    "total_pages": 3,
                },
            },
        )
        # responses.get(
        #     f"{self.BASE_URL}/mails/",
        #     status=403,
        #     json={"error": {"message": "権限がありません"}},
        # )
        # responses.get(
        #     f"{self.BASE_URL}/mails/",
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
        response = requests.get(urljoin(self.BASE_URL, "/mails/"), params=params)
        return ApiResult(response)

    @responses.activate  # WARNING: モック
    def get_mail_detail(self, mail_id: int) -> ApiResult:
        # WARNING: モック
        responses.get(
            f"{self.BASE_URL}/mails/1/",
            status=200,
            json={"mail": {"id": "1", "type": "メールA---", "title": "タイトル1", "sent_at": "2021/01/01"}},
        )
        # responses.get(
        #     f"{self.BASE_URL}/mails/1/",
        #     status=403,
        #     json={"error": {"message": "権限がありません"}},
        # )
        # responses.get(
        #     f"{self.BASE_URL}/mails/1/",
        #     status=404,
        #     json={"error": {"message": "メールが見つかりませんでした"}},
        # )
        # responses.get(
        #     f"{self.BASE_URL}/mails/1/",
        #     status=500,
        #     json={"error": {"message": "処理が失敗しました"}},
        # )

        response = requests.get(urljoin(self.BASE_URL, f"/mails/{mail_id}/"))
        return ApiResult(response)

    @responses.activate  # WARNING: モック
    def post_mail(self, type_: str, title: str, text: str) -> ApiResult:
        # WARNING: モック
        # responses.post(
        #     f"{self.BASE_URL}/mails/",
        #     status=200,
        #     json={"mail": {"id": "1", "type": "メールA", "title": "タイトル1", "sent_at": "2021/01/01"}},
        # )
        responses.post(
            f"{self.BASE_URL}/mails/",
            status=400,
            json={
                "validation": True,
                "errors": {
                    "non_field_error": [
                        "フィールド以外のエラーメッセージです1",
                        "フィールド以外のエラーメッセージです2",
                    ],
                    "type": ["メール種別のエラーメッセージです1", "メール種別のエラーメッセージです2"],
                    "title": ["メール件名のエラーメッセージです1", "メール件名のエラーメッセージです2"],
                    "text": ["メール本文のエラーメッセージです"],
                },
            },
        )

        response = requests.post(
            urljoin(self.BASE_URL, "/mails/"),
            data={"type": type_, "title": title, "text": text},
        )
        return ApiResult(response)
