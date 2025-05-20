from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.urls import reverse
from django.views import View

from common.view_mixin import (
    BaseViewMixin,
    LoginRequiredAnyMixin,
)


class TopView(LoginRequiredAnyMixin, BaseViewMixin, View):
    def get(self, _):
        if not (user := self.session.user):
            return HttpResponseRedirect(resolve_url(settings.LOGIN_URL))

        # TODO: リソースにロジック移動
        match user.type:
            case "pro":
                return HttpResponseRedirect(reverse("user:pro-users"))
            case "admin":
                return HttpResponseRedirect(reverse("user:admin-users"))
            case "contractor":
                return HttpResponseRedirect(reverse("user:contractors"))
            case _:
                raise ValueError(f"Invalid type: {user.type}")
