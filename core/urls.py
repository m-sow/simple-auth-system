from django.urls import path

from core.views import LoginView, SignUpView, IndexPage, LogoutView, ChangeLanguageView, ActivationView

app_name = 'core'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),

    path('register/', SignUpView.as_view(), name='register'),
    path('', IndexPage.as_view(), name='index'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('language/', ChangeLanguageView.as_view(), name='change_language'),

    path('activate/<code>', ActivationView.as_view(), name='activate')
]
