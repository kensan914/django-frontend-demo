from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from common.api.api_client import ApiClient
from common.states.pagination_state import PaginationState
from common.states.sort_state import SortState
from common.view_mixin import BaseViewMixin
from mail.forms import MailForm, SearchMailForm


class IndexView(BaseViewMixin, TemplateView):
    template_name = "mail/index.html"

    def get_context_data(self, **kwargs):
        search_form = SearchMailForm(self.request.GET)
        if search_form.is_valid():
            q = search_form.cleaned_data["q"]
        else:
            search_form = SearchMailForm()
            q = None

        api_result = ApiClient().get_mails(
            q=q,
            sort=self.request.GET.get("sort"),
            page=self.request.GET.get("page"),
        )
        if api_result.error:
            self.handle_general_error(api_result)

        context = super().get_context_data(**kwargs)
        context["search_form"] = search_form
        context["mails"] = api_result.response_data["mails"]
        context["sort_state"] = SortState(self.request)
        context["pagination_state"] = PaginationState(api_result.response_data["pagination"], request=self.request)
        return context


class DetailView(BaseViewMixin, TemplateView):
    template_name = "mail/detail.html"

    def get_context_data(self, mail_id: int, **kwargs):
        api_result = ApiClient().get_mail_detail(mail_id)
        if api_result.error:
            self.handle_general_error(api_result)

        context = super().get_context_data(**kwargs)
        context["mail"] = api_result.response_data["mail"]
        return context


class NewView(BaseViewMixin, FormView):
    template_name = "mail/new.html"
    form_class = MailForm
    success_url = reverse_lazy("mail:index")

    def form_valid(self, form: MailForm):
        api_result = ApiClient().post_mail(
            type_=form.cleaned_data["type"],
            title=form.cleaned_data["title"],
            text=form.cleaned_data["text"],
        )
        if api_result.error:
            if api_result.error.is_validation:
                form = self.add_api_validation_error(form, api_result.error)
                return super().form_invalid(form)
            self.handle_general_error(api_result)

        messages.success(self.request, "登録内容を保存しました。")
        return super().form_valid(form)
