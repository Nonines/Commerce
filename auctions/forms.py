from django.forms import ModelForm
from .models import Listing, Bid, Comment


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "image", "category"]


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["offer"]


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
