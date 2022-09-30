from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_item, name="create"),
    path("listing/<int:item_id>/", views.listing, name="listing"),
    path("bidding/", views.bidding, name="bid"),
    path("status/", views.bid_status, name="status"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("comments/", views.comments, name="comments"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
]
