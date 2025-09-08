from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from common.view_mixin import BaseViewMixin, LoginRequiredAnyMixin
from login.forms import LoginForm


class LoginView(BaseViewMixin, DjangoLoginView):
    template_name = "login/login.html"
    form_class = LoginForm
    next_page = "top:top"
    required_api_csrf = True

    def form_valid(self, form: LoginForm):
        # NOTE: DjangoLogoutView では django.contrib.auth.login() しているため、ログイン API を叩くようにオーバーライド
        api_result = self.api_client.post_login(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if api_result.error:
            if api_result.error.is_validation:
                form = self.add_api_validation_error(form, api_result.error)
                return super().form_invalid(form)
            self.handle_general_error(api_result)

        if session_cookie_params := api_result.get_session_cookie_params():
            response = HttpResponseRedirect(self.get_success_url())
            response.set_cookie(
                settings.SESSION_COOKIE_NAME,
                **session_cookie_params,
            )
            messages.success(self.request, "ログインしました。")
            return response

        return super().form_invalid(form)


# TODO: ログイン不要にできないか
class LogoutView(LoginRequiredAnyMixin, BaseViewMixin, DjangoLogoutView):
    template_name = "login/logged_out.html"
    # NOTE: DjangoLogoutView では get も受け付けているが、非推奨で削除される想定のため、今回は post のみ受け付けるようにする
    http_method_names = ["post", "options"]
    required_api_csrf = True

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # NOTE: DjangoLogoutView では django.contrib.auth.logout() しているため、ログアウト API を叩くようにオーバーライド
        #       また、DjangoLogoutView では RedirectURLMixin による動的なリダイレクトURL決定処理が行われているが、今回ログアウトではリダイレクトしないため、その処理は行わない
        api_result = self.api_client.post_logout()
        if api_result.error:
            self.handle_general_error(api_result)

        self.clear_session()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
