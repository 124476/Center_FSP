from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import FormView, CreateView
import django.views.generic

from users.forms import UserForm, UserRegionForm, RegionalRepresentativeSignupForm
from users.models import User


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

    def get(self, request, *args, **kwargs):
        translation.activate(request.LANGUAGE_CODE)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем переводы для заголовка и кнопки
        context["title"] = _("Register Regional Representative")
        context["submit_text"] = _("Register")
        return context

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
    queryset = User.objects.exclude(is_superuser=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Представители"
        return context


class UserDetailView(DetailView):
    model = User
    template_name = "users/user_detail.html"
    context_object_name = "personal"

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Проверяем, является ли текущий пользователь суперюзером
        if self.request.user.is_superuser:
            context["region_form"] = UserRegionForm(instance=self.object)

        return context


# Обработка изменения региона пользователя
def update_user_region(request, pk):
    user = get_object_or_404(User, pk=pk)

    # Проверяем, является ли текущий пользователь суперюзером
    if not request.user.is_superuser:
        messages.error(request, "У вас нет прав на выполнение этого действия.")
        return redirect('users:user_detail', pk=pk)

    if request.method == "POST":
        form = UserRegionForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Регион пользователя успешно обновлен.")
        else:
            messages.error(request, "Ошибка при обновлении региона.")
    return redirect('users:user_detail', pk=pk)

# Обработка удаления региона
def remove_user_region(request, pk):
    user = get_object_or_404(User, pk=pk)

    # Проверяем права суперюзера
    if not request.user.is_superuser:
        messages.error(request, "У вас нет прав на выполнение этого действия.")
        return redirect('users:user_detail', pk=pk)

    user.region = None
    user.save()
    messages.success(request, "Регион был успешно удален.")
    return redirect('users:user_detail', pk=pk)