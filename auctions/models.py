from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# User model:
class User(AbstractUser):
    pass

    def __str__(self) -> str:
        return self.username


# Auction listing model:
class Listing(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name="own_goods")

    title = models.CharField(max_length=32)
    description = models.TextField()
    starting_bid = models.IntegerField()
    image = models.URLField()
    category = models.CharField(max_length=24, null=True, blank=True)

    def __str__(self) -> str:
        return self.title


# Bidding model:
class Bid(models.Model):
    is_open = models.BooleanField(default=True)

    listing = models.ForeignKey(Listing,
                                on_delete=models.CASCADE,
                                related_name="bid_listing")

    seller = models.ForeignKey(Listing,
                               on_delete=models.CASCADE,
                               related_name="bid_seller")

    starting_bid = models.IntegerField()
    offer = models.IntegerField()

    bidder = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name="bidding_for")

    offer_count = models.IntegerField()


# Comments model:
class Comment(models.Model):
    item = models.ForeignKey(Listing,
                             on_delete=models.CASCADE,
                             related_name="comments")

    comment = models.TextField(max_length=128, null=False, blank=False)

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name="commenter")

    last_modified = models.DateTimeField(auto_now=True)


# Watchlist model:
class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="watchlist_owned")

    listings = models.ManyToManyField(Listing,
                                      related_name="watchlist_in")
