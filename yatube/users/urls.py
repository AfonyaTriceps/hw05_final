from django.contrib.auth import views as vw
from django.urls import path, reverse_lazy

from users.apps import UsersConfig
from users.views import SignUp

app_name = UsersConfig.name

urlpatterns = [
    path(
        'logout/',
        vw.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout',
    ),
    path('signup/', SignUp.as_view(), name='signup'),
    path(
        'login/',
        vw.LoginView.as_view(template_name='users/login.html'),
        name='login',
    ),
    path(
        'password_change/',
        vw.PasswordChangeView.as_view(
            success_url=reverse_lazy('users:password_change_done'),
            template_name='users/password_change_form.html',
        ),
        name='password_change',
    ),
    path(
        'password_change/done/',
        vw.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html',
        ),
        name='password_change_done',
    ),
    path(
        'password_reset/',
        vw.PasswordResetView.as_view(
            success_url=reverse_lazy('users:password_reset_done'),
            template_name='users/password_reset_form.html',
            email_template_name='users/password_reset_email.html',
        ),
        name='password_reset',
    ),
    path(
        'password_reset/done/',
        vw.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'password_reset_confirm/<uidb64>/<token>/',
        vw.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'password_reset/complete/',
        vw.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]
