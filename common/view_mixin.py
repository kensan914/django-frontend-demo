from django.core.exceptions import PermissionDenied
from django.forms import Form
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from common.api.api_errors import ApiValidationError
from common.api.api_results import ApiResult


class BaseViewMixin:
    """View に共通する振る舞いや処理を定義した Mixin
    WARNING: 一部 django.views.View のメソッドをオーバーライドしているため、継承時に一番左に記載してください
             ex) class MyView(BaseViewMixin, TemplateView):
    """

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        """never_cache で全ての HTTP メソッドに対してキャッシュを無効化する（Django Admin の View のデフォルト動作）
        レスポンスヘッダ `Expires`,`Cache-Control` を修正する (https://docs.djangoproject.com/ja/4.2/topics/http/decorators/#django.views.decorators.cache.never_cache )  # noqa E501
        """
        return super().dispatch(*args, **kwargs)

    def handle_general_error(self, api_result: ApiResult) -> None:
        if api_result.error:
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
