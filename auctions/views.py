from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing


# Default page:
def index(request):
    # When this view is called, retrieve all objects(data in database fields)
    # from the Listing table by constructing a QuerySet, and passing it as
    # context to the rendered template
    listings = Listing.objects.all()

    return render(request,
                  "auctions/index.html", {"listings": listings})


# View for each Individual listing:
def item(request, item_id):
    # This query set retrives a specific Listing (in database table 'Listing')
    # that corresponds to the primary key of the object in the database
    listing = Listing.objects.get(pk=item_id)
    item_name = listing.title

    return render(request,
                  "auctions/listing.html",
                  {"title": item_name, "listing": listing})


# User Authentication:
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
