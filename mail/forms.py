from django import forms


class SearchMailForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"autofocus": True}),
    )


class MailForm(forms.Form):
    type = forms.ChoiceField(
        label="メール種別",
        choices=[
            ("mail_a", "メールA"),
            ("mail_b", "メールB"),
            ("mail_c", "メールC"),
        ],
    )
    title = forms.CharField(
        label="メール件名",
        widget=forms.TextInput(attrs={"size": 40}),
    )
    text = forms.CharField(
        label="メール本文",
        widget=forms.Textarea(attrs={"size": 40}),
    )
