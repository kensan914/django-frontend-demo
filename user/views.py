from django.views.generic import TemplateView

from common.view_mixin import (
    BaseViewMixin,
    LoginRequiredAdminMixin,
    LoginRequiredContractorMixin,
    LoginRequiredProMixin,
)


class ProUsersIndexView(LoginRequiredProMixin, BaseViewMixin, TemplateView):
    template_name = "user/index.html"

    def get_context_data(self, **kwargs):
        api_result = self.api_client.get_pro_users()
        if api_result.error:
            self.handle_general_error(api_result)

        context = super().get_context_data(**kwargs)
        context["users"] = api_result.response_data
        context["title"] = "プロユーザ一覧"
        return context


class AdminUsersIndexView(LoginRequiredAdminMixin, BaseViewMixin, TemplateView):
    template_name = "user/index.html"

    def get_context_data(self, **kwargs):
        api_result = self.api_client.get_admin_users()
        if api_result.error:
            self.handle_general_error(api_result)

        context = super().get_context_data(**kwargs)
        context["users"] = api_result.response_data
        context["title"] = "管理者ユーザ一覧"
        return context


class ContractorsIndexView(LoginRequiredContractorMixin, BaseViewMixin, TemplateView):
    template_name = "user/index.html"

    def get_context_data(self, **kwargs):
        api_result = self.api_client.get_contractors()
        if api_result.error:
            self.handle_general_error(api_result)

        context = super().get_context_data(**kwargs)
        context["users"] = api_result.response_data
        context["title"] = "契約者一覧"
        return context
