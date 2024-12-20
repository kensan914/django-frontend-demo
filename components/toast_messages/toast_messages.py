from django_components import Component, register


@register("toast_messages")
class ToastMessages(Component):
    template_name = "toast_messages/template.html"

    def get_context_data(self, messages):
        return {
            "messages": messages,
        }
