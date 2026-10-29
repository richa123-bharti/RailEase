from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    dashboard,
    demo_wallet_payment,
    register,
    verify_wallet_payment,
    wallet_payment_order,
)

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("wallet/order/", wallet_payment_order, name="wallet_payment_order"),
    path("wallet/verify/", verify_wallet_payment, name="verify_wallet_payment"),
    path("wallet/demo/", demo_wallet_payment, name="demo_wallet_payment"),
]
