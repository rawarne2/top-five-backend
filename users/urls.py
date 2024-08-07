from django.urls import path
from . import views


urlpatterns = [
    path("potential_partners/", views.get_potential_partners,
         name="potential_partners"),
    path("user_by_id/<int:user_id>/", views.get_user, name="user_by_id"),
    path("update_user/<int:user_id>/", views.update_user, name="update_user"),
    path("delete_user/<int:user_id>/", views.delete_user, name="delete_user"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup_view, name="signup"),
    path("change_password/", views.change_password, name="change_password"),
    path("reset_password/", views.reset_password, name="reset_password"),
    path("get_profile/<int:user_id>/", views.get_profile, name="get_profile"),
    path("update_profile/<int:user_id>/",
         views.create_or_update_profile, name="update_profile"),
    path("create_profile/<int:user_id>/", views.create_or_update_profile,
         name="create_or_update_profile"),
]
