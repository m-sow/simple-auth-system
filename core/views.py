from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.utils.crypto import get_random_string
from django.views.generic import FormView, View, TemplateView

from django.contrib.auth.views import (
    LogoutView as BaseLogoutView
)

from authentication_system.utils import send_activation_email
from core.forms import SignInViaUsernameForm, SignInViaEmailForm, SignInViaEmailOrUsernameForm, SignUpForm
from core.models import Activation

from django.utils.translation import gettext_lazy as _


class GuestOnlyVew(View):
    def dispatch(self, request, *args, **kwargs):
        # Redirect to the index page if the user is already authenticated
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        return super().dispatch(request, *args, **kwargs)


class LoginView(GuestOnlyVew, FormView):
    template_name = "login.html"

    @staticmethod
    def get_form_class(**kwargs):
        if settings.DISABLE_USERNAME or settings.LOGIN_VIA_EMAIL:
            return SignInViaEmailForm

        if settings.LOGIN_VIA_EMAIL_OR_USERNAME:
            return SignInViaEmailOrUsernameForm

        return SignInViaUsernameForm

    def form_valid(self, form):
        request = self.request

        if settings.USE_REMEMBER_ME:
            if not form.cleaned_data['remember_me']:
                request.session.set_expiry(0)

        login(request, form.user_cache)

        return redirect(settings.LOGIN_REDIRECT_URL)


class SignUpView(GuestOnlyVew, FormView):
    template_name = 'register.html'
    form_class = SignUpForm

    def form_valid(self, form):
        request = self.request
        user = form.save(commit=False)

        if settings.DISABLE_USERNAME:
            # Set a temporary username
            user.username = get_random_string()
        else:
            user.username = form.cleaned_data['username']

        if settings.ENABLE_USER_ACTIVATION:
            user.is_active = False

        user.save()

        # Change the username to the "user_ID" form
        if settings.DISABLE_USERNAME:
            user.username = f'user_{user.id}'
            user.save()

        if settings.ENABLE_USER_ACTIVATION:
            code = get_random_string(20)

            act = Activation()
            act.code = code
            act.user = user
            act.save()

            send_activation_email(request, user.email, code)

            messages.success(request, _('You are signed up. To active the account, follow the link sent to the mail.'))

        else:
            raw_password = form.cleaned_data['password1']

            user = authenticate(username=user.username, password=raw_password)
            login(request, user)

            messages.success(request, _('You are successfully signed up !'))

        return redirect('core:index')


class LogoutView(LoginRequiredMixin, BaseLogoutView):
    template_name = 'logout.html'


class IndexPage(TemplateView):
    template_name = 'index.html'


class ChangeLanguageView(TemplateView):
    template_name = 'change_language.html'


class ActivationView(View):

    @staticmethod
    def get(request, code):
        act = get_object_or_404(Activation, code=code)

        # Activate profile
        user = act.user
        user.is_active = True
        user.save()

        # Remove the activation record
        act.delete()

        messages.success(request, _('You have successfully activated your account !'))

        return redirect('core:login')
