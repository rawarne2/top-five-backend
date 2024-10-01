from django.urls import path
from . import views


urlpatterns = [
    path("potential_matches/", views.get_potential_matches,
         name="potential_matches"),

    path("signup/", views.create_user, name="signup"),
    path("user_by_id/<int:user_id>/", views.get_user, name="user_by_id"),
    path("update_user/<int:user_id>/", views.update_user, name="update_user"),
    path("delete_user/<int:user_id>/", views.delete_user, name="delete_user"),

    path("update_profile/<int:user_id>/",
         views.update_profile, name="update_profile"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("change_password/", views.change_password, name="change_password"),
    path("reset_password/", views.reset_password, name="reset_password"),
    path("get_profile/<int:user_id>/", views.get_profile, name="get_profile"),

    path('get_presigned_urls/<int:user_id>/',
         views.get_presigned_urls, name='get_presigned_urls'),
]
