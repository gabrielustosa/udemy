from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView

from udemy.apps.user.forms import UserCreateForm


class UserRegisterView(CreateView):
    template_name = 'registration/../../../templates/registration/register.html'
    form_class = UserCreateForm
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if not settings.ALLOW_REGISTRATION:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(
            username=cd['username'],
            password=cd['password1']
        )
        login(request=self.request, user=user)
        return result
