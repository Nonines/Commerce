from django.contrib import admin

from .models import User, Listing, Bid, Watchlist, Comment


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "last_login")


class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "starting_bid", "category", "seller_id")


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "is_open", "starting_bid", "offer_count")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author_id", "item_id", "content", "date_published")


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Watchlist)
admin.site.register(Comment, CommentAdmin)
