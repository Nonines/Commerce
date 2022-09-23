from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

    def __str__(self) -> str:
        return self.username


# one for bids,
class Bid(models.Model):
    starting_bid = models.IntegerField()


# Auction listing model:
class Listing(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="goods")
    title = models.CharField(max_length=32)
    description = models.TextField()
    starting_bid = models.IntegerField()
    image = models.URLField(null=True, blank=True)
    category = models.CharField(max_length=24, null=True, blank=True)

    def __str__(self) -> str:
        return self.title


# and one for comments made on auction listings.
