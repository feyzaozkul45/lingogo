from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label='E-posta')
    field_order = ['username', 'email', 'password1', 'password2']

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Bu e-posta adresi zaten kullanılıyor.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    """Giriş alanına kullanıcı adı ya da e-posta yazılabilir.

    E-posta ancak tek bir hesapla eşleşiyorsa ve aynı yazımda bir kullanıcı adı
    yoksa kullanıcı adına çevrilir; aksi halde normal kullanıcı adı girişi gibi
    davranır (belirsiz e-postayla giriş yapılmaz).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Kullanıcı adı veya e-posta'

    def clean(self):
        identifier = (self.cleaned_data.get('username') or '').strip()
        if '@' in identifier and not User.objects.filter(username=identifier).exists():
            matches = list(User.objects.filter(email__iexact=identifier)[:2])
            if len(matches) == 1:
                self.cleaned_data['username'] = matches[0].get_username()
        return super().clean()
