from allauth.account.forms import AddEmailForm, LoginForm, SignupForm, \
    ChangePasswordForm, ResetPasswordForm, ResetPasswordKeyForm
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext as _

from users.models import User, Region


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if len(self.visible_fields()) == 1:
            self.visible_fields()[0].field.widget.attrs[
                "class"
            ] = "form-control input-field-only-one"
        else:
            for field in self.visible_fields():
                field.field.widget.attrs["class"] = "form-control input-field"
                if isinstance(field.field.widget, forms.CheckboxInput):
                    field.field.widget.attrs["class"] = "form-check-input"

        self.update_errors_class()

    def update_errors_class(self):
        for field in self.visible_fields():
            if self.errors.get(field.name):
                if "is-invalid" not in field.field.widget.attrs["class"]:
                    field.field.widget.attrs["class"] += " is-invalid"

    def add_error(self, field, error):
        super().add_error(field, error)
        self.update_errors_class()


class UserForm(BootstrapFormMixin, UserChangeForm):
    password = None

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields[User.email.field.name].widget.attrs["readonly"] = True
        self.fields[User.email.field.name].widget.attrs["disabled"] = True
        self.fields[User.avatar.field.name].widget.attrs["class"] += " d-none"

    class Meta(UserChangeForm.Meta):
        model = get_user_model()

        fields = [
            User.username.field.name,
            User.email.field.name,
            User.avatar.field.name,
        ]


class RegionalRepresentativeSignupForm(BootstrapFormMixin, SignupForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        required=True,
        label=_("Region"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    first_name = forms.CharField(
        required=True,
        label=_("First Name"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("Enter your first name")}),
    )
    last_name = forms.CharField(
        required=True,
        label=_("Last Name"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("Enter your last name")}),
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.region = self.cleaned_data["region"]
        user.save()
        return user


class RegionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Region
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class EmailForm(BootstrapFormMixin, AddEmailForm):
    pass


class LoginForm(BootstrapFormMixin, LoginForm):
    pass


class ChangePasswordForm(BootstrapFormMixin, ChangePasswordForm):
    pass


class ResetPasswordForm(BootstrapFormMixin, ResetPasswordForm):
    pass


class ResetPasswordKeyForm(BootstrapFormMixin, ResetPasswordKeyForm):
    pass
