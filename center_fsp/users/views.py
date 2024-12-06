from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView, CreateView
import django.views.generic

from users.forms import UserForm
from users.models import User

from users.forms import RegionalRepresentativeSignupForm


class AccountView(LoginRequiredMixin, FormView):
    template_name = "users/profile.html"
    form_class = UserForm

    def get_initial(self):
        return {
            "username": self.request.user.username,
            "email": self.request.user.email,
            "avatar": self.request.user.avatar,
        }

    def post(self, request, *args, **kwargs):
        post = request.POST.copy()
        post["email"] = request.user.email
        user_form = UserForm(post, request.FILES, instance=request.user)
        new_username = user_form.cleaned_data.get("username")

        if new_username != request.user.username:
            if user_form.is_valid():
                if User.objects.filter(username=new_username).exists():
                    user_form.add_error(
                        "username",
                        _("username_is_already_taken"),
                    )
        elif user_form.is_valid():
            user_form.save()
            return redirect("users:profile")

        return render(request, "users/profile.html", {"form": user_form})


class PasswordChangeDoneView(views.PasswordChangeDoneView):
    pass


@method_decorator(staff_member_required, name="dispatch")
class RegionalRepresentativeSignupView(CreateView):
    model = User
    form_class = RegionalRepresentativeSignupForm
    template_name = "users/signup.html"
    success_url = reverse_lazy("homepage:main")

    def form_valid(self, form):
        user = form.save(request=self.request)
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.region = form.cleaned_data["region"]
        user.is_staff = False
        user.save()
        return redirect("homepage:main")

@method_decorator(staff_member_required, name="dispatch")
class UsersView(django.views.generic.ListView):
    template_name = "users/list_users.html"
    context_object_name = "users"
    queryset = User.objects.exclude(region=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Представители"
        return context


__all__ = ()
