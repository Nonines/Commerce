from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

    def __str__(self) -> str:
        return f"U'name: {self.username}, Name: {self.first_name}"


# one for bids,
class Bid(models.Model):
    starting_bid = models.IntegerField()


# Auction listing model:
class Listing(models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField()
    starting_bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    image = models.URLField()
    category = models.CharField(max_length=24)

    def __str__(self) -> str:
        return f"Title: {self.title}"


# and one for comments made on auction listings.
