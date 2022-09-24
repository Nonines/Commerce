from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    pass

    def __str__(self) -> str:
        return self.username


# one for bids,
class Bid(models.Model):
    starting_bid = models.IntegerField()


# Auction listing model:
class Listing(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name="own_goods")

    title = models.CharField(max_length=32)
    description = models.TextField()
    starting_bid = models.IntegerField()
    image = models.URLField(default="shorturl.at/KM139")
    category = models.CharField(max_length=24, null=True, blank=True)

    def __str__(self) -> str:
        return self.title


# and one for comments made on auction listings.

# Watchlist model:
