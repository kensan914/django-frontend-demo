from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest

from common.exceptions import Unauthorized


class RedirectToLoginMiddleware:
    """TODO"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request: HttpRequest, exception):
        if not isinstance(exception, Unauthorized):
            return None

        # NOTE: ログイン画面への HttpResponseRedirect を生成するために、login_required デコレータに使われている user_passes_test のロジックを流用する
        user_passes_test_decorator = user_passes_test(
            # NOTE: 無条件でログイン画面への HttpResponseRedirect を生成させる
            test_func=lambda _: False
        )

        def dummy_view_func(_):
            return None

        user_passes_test_view_func = user_passes_test_decorator(dummy_view_func)
        redirect_response = user_passes_test_view_func(request)
        return redirect_response
