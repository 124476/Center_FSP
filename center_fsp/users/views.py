from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import FormView, CreateView
import django.views.generic

from users.forms import UserForm, RegionForm
from users.models import User, Region

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

    def form_valid(self, form):
        user = form.save(request=self.request)
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.region = form.cleaned_data["region"]
        user.is_staff = False
        user.save()
        return redirect("users:users")


@method_decorator(staff_member_required, name="dispatch")
class UsersView(django.views.generic.ListView):
    template_name = "users/list_users.html"
    context_object_name = "users"
    queryset = User.objects.exclude(region=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Представители"
        return context


@method_decorator(staff_member_required, name="dispatch")
class NewRegionView(CreateView):
    model = Region
    form_class = RegionForm
    template_name = "users/new_region.html"
    success_url = reverse_lazy("users:users")

    def form_valid(self, form):
        return super().form_valid(form)


class UserDetailView(DetailView):
    model = User
    template_name = "users/user_detail.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs["pk"])


__all__ = ()
