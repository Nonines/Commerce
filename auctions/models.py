from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# User model:
class User(AbstractUser):
    pass

    def __str__(self) -> str:
        return self.username


# Bidding model:
class Bid(models.Model):
    listing = models.CharField()
    seller = models.CharField()
    starting_bid = models.IntegerField()

    first_offer = models.IntegerField(null=True, blank=True)
    new_offer = models.IntegerField()
    offer_count = models.IntegerField()


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


# and one for comments made on auction listings.

# Watchlist model:
class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="watchlist_owned")
    listings = models.ManyToManyField(Listing,
                                      related_name="watchlist_in")
