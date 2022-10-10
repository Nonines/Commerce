from django.forms import ModelForm
from .models import Listing, Bid, Comment
from django import forms


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "image", "category"]
        labels = {
            "title": "",
            "description": "",
            "starting_bid": "",
            "image": "",
            "category": ""
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "id": "title1",
                "placeholder": "Listing title"
            }),
            "description": forms.Textarea(attrs={
                "id": "description1",
                "placeholder": "Description",
                "style": "resize:none;"
            }),
            "starting_bid": forms.NumberInput(attrs={
                "id": "starting_bid1",
                "placeholder": "Starting bid"
            }),
            "image": forms.URLInput(attrs={
                "id": "image1",
                "placeholder": "Image link"
            }),
            "category": forms.TextInput(attrs={
                "id": "category1",
                "placeholder": "Category"
            }),
        }


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["offer"]
        labels = {
            "offer": ""
        }
        widgets = {
            "offer": forms.NumberInput(attrs={
                "id": "offer",
                "placeholder": "Input offer here"
            })
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        labels = {
            "content": ""
        }
        widgets = {
            "content": forms.Textarea(attrs={
                "id": "content",
                "placeholder": "Write something...",
                "style": "resize:none;"
            })
        }
