from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(label="メールアドレス", max_length=255)
    password = forms.CharField(label="パスワード", widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        # TODO: AuthenticationForm 参考
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
