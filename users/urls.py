from django.urls import path

from . import views

urlpatterns = [
    path("all/", views.get_all_users, name="all"),
    path("user_by_id/<int:user_id>/", views.get_user, name="user_by_id"),
    path("update_user/<int:user_id>/", views.update_user, name="update_user"),
    path("delete_user/<int:user_id>/", views.delete_user, name="delete_user"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup_view, name="signup"),
    path("change_password/", views.change_password, name="change_password"),
    path("reset_password/", views.reset_password, name="reset_password"),
]
