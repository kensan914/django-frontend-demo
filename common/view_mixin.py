from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.forms import Form
from django.http import Http404, HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from common.api.api_client import ApiClient
from common.api.api_errors import ApiValidationError
from common.api.api_resources.session import Session, User
from common.api.api_results import ApiResult
from common.exceptions import Unauthorized


class BaseViewMixin:
    """View に共通する振る舞いや処理を定義した Mixin
    WARNING: 一部 django.views.View のメソッドをオーバーライドしているため、継承時に一番左に記載してください
             ex) class MyView(BaseViewMixin, TemplateView):
    TODO: 下書き
    - 直接 ApiClient をインスタンス化して使うのではなく、この mixin を継承して self.api_client を使うようにする
    - できること: self.session へのアクセス、template 内の session context へのアクセス
    """

    # NOTE: アクセス可能とするユーザタイプ（複数指定可）
    #       指定された場合ログイン必須、指定されなかった場合ログイン不要の View として扱われる
    #       このクラス変数は直接指定せず、後述の LoginRequiredXXXMixin を使用する
    user_types_required_login: tuple[User.Type] = tuple()

    # NOTE: ログイン不要の View でも CSRF 検証を必要とする API にリクエストしたい場合、True を指定する（ex. ログイン画面）
    #       ログイン必須の View の場合、この設定に関わらず、CSRF 検証を必要とする API にリクエストするためのセットアップを自動で行う
    required_api_csrf: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.api_client = ApiClient()
        # NOTE: 後述のセッション取得 API リクエスト後にセットする（ログイン不要かつ、API の CSRF 検証不要の場合は None のまま）
        self._session: Session | None = None

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if self._required_login:
            self._authenticate_api_client(request)
        if self._required_login or self.required_api_csrf:
            self._setup_session_and_csrf()

    # NOTE: never_cache で全ての HTTP メソッドに対してキャッシュを無効化する（Django Admin の View のデフォルト動作）
    #       レスポンスヘッダ `Expires`,`Cache-Control` を修正する (https://docs.djangoproject.com/ja/4.2/topics/http/decorators/#django.views.decorators.cache.never_cache )
    @method_decorator(never_cache)
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if not hasattr(super(), "get_context_data"):
            return kwargs
        context = super().get_context_data(**kwargs)
        if self._session:
            context["session"] = self._session
        return context

    @property
    def session(self) -> Session:
        if not self._session:
            raise AssertionError(
                "セッション取得 API リクエストが行われていないため、self.session にアクセスできません。"
                "ログイン必須にするか、API の CSRF 検証のセットアップを行うようにしてください。"
            )
        return self._session

    def clear_session(self) -> None:
        self._session = None

    def handle_general_error(self, api_result: ApiResult) -> None:
        if api_result.error:
            if api_result.is_401:
                # NOTE: ログイン画面にリダイレクト
                raise Unauthorized(api_result.error.response_data)
            if api_result.is_403:
                # NOTE: templates/403.html をレンダリング
                raise PermissionDenied(api_result.error.response_data)
            if api_result.is_404:
                # NOTE: templates/404.html をレンダリング
                raise Http404(api_result.error.response_data)
            # NOTE: templates/500.html をレンダリング
            raise Exception(api_result.error.response_data)

    def add_api_validation_error(
        self,
        form: Form,
        api_validation_error: ApiValidationError,
    ) -> Form:
        """引数で受け取った form インスタンスに対して、API のバリデーションエラーを `add_error` で追加する
        これにより、API から渡されたバリデーションエラーメッセージをフォームに表示できる
        """

        for error_message in api_validation_error.non_field_error_messages:
            form.add_error(None, error_message)

        for (
            field_name,
            error_messages,
        ) in api_validation_error.field_error_messages_dict.items():
            for error_message in error_messages:
                form.add_error(field_name, error_message)

        return form

    @property
    def _required_login(self) -> bool:
        """ログイン必須の View かどうか"""
        return len(self.user_types_required_login) > 0

    def _authenticate_api_client(self, request: HttpRequest) -> None:
        """API クライアントにセッション ID をセットし、認証を必要とする API リクエストを行えるようにする"""
        if not (session_id := request.COOKIES.get(settings.SESSION_COOKIE_NAME)):
            # NOTE: ログイン画面にリダイレクト
            raise Unauthorized(
                "ログイン必須の画面ですがクッキーにセッションIDが存在しないため、処理を中断します。"
            )

        self.api_client.set_session_id(session_id)

    def _setup_session_and_csrf(self) -> None:
        """self.session に API から取得したセッション情報をセットし、加えて CSRF 検証を必要とする API リクエストを行えるようにする
        FYI: CSRF 検証を必要とする API？ -> 認証が必要でかつ POST/PUT/PATCH/DELETE のいずれかのメソッド (https://www.django-rest-framework.org/topics/ajax-csrf-cors/#csrf-protection )
        """
        session_api_result = self.api_client.get_session_and_set_csrf_cookie()
        if session_api_result.error:
            self.handle_general_error(session_api_result)

        self._session = Session(session_api_result)

        if (
            self._session.user
            and self._required_login
            and self._session.user.type not in self.user_types_required_login
        ):
            # NOTE: templates/403.html をレンダリング
            raise PermissionDenied(
                "現在ログイン中のユーザが、アクセスを許可されていないユーザタイプのため、処理を中断します。"
            )

        self.api_client.set_csrf_token(self._session.csrf_token)


class LoginRequiredAnyMixin:
    user_types_required_login = tuple(User.Type.values)


class LoginRequiredProMixin:
    user_types_required_login = (User.Type.PRO,)


class LoginRequiredAdminMixin:
    user_types_required_login = (User.Type.ADMIN,)


class LoginRequiredContractorMixin:
    user_types_required_login = (User.Type.CONTRACTOR,)
