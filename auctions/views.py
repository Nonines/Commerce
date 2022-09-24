from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.core.exceptions import ObjectDoesNotExist

from .models import User, Listing, Watchlist
from .forms import ListingForm


# View for creating a new listing
@login_required(login_url="login")
def create_item(request):
    # if this is a post request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request
        form = ListingForm(request.POST)

        # check whether the form instance is valid
        if form.is_valid():
            # if it is, retrieve the cleaned data
            title = form.cleaned_data["title"]
            desc = form.cleaned_data["description"]
            st_bid = form.cleaned_data["starting_bid"]
            image = form.cleaned_data["image"]
            category = form.cleaned_data["category"]

            # get the current user to set it as the seller
            user_id = request.user.id
            current_user = User.objects.get(pk=user_id)

            # create a new Listing instance and save the data to the database
            new_item = Listing(seller=current_user, title=title,
                               description=desc, starting_bid=st_bid,
                               image=image, category=category)
            new_item.save()

            # redirect to the listing's page
            return HttpResponseRedirect(reverse("listing", args=[new_item.pk]))

        # if the form isn't valid, re-render it with existing data
        else:
            return render(request,
                          "auctions/create_listing.html", {"form": form})

    # If it is a get request, render the page with the form
    form = ListingForm
    return render(request,
                  "auctions/create_listing.html", {"form": form})


# View for watchlists
@login_required(login_url="login")
def watchlist(request):
    # Get the current user's instance
    user_id = request.user.id
    current_user = User.objects.get(pk=user_id)

    # get the current user's watchlist
    watchlist = current_user.watchlist_owned.get()
    print(watchlist)

    if request.method == "POST":
        form = request.POST
        if form["state"] == "Add":
            pass
        elif form["state"] == "Remove":
            pass
        return render(request, "auctions/watchlist.html")

    # If it is a get request, get the current user's Watchlist
    else:
        try:
            user_watchlist = Watchlist.objects.get(user=current_user)

        # Adds a watchlist field for the user in the database
        except ObjectDoesNotExist:
            try:
                # And displays a message for the user
                Watchlist.objects.create(user=current_user)
                return render(request, "auctions/watchlist.html",
                              {"message": "Watchlist is empty!"})
            except IntegrityError:
                print("Integrity error")
                return render(request, "auctions/watchlist.html")

        # If there are no errors, display all the items in the user's wishlist
        watchlist_items = user_watchlist.listings.all()
        return render(request, "auctions/watchlist.html",
                      {"watchlist": watchlist_items})


# Default page (displays all the listings):
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

    # Gets the current user and items in their watchlist
    user_id = request.user.id
    current_user = User.objects.get(pk=user_id)
    user_watchlist = Watchlist.objects.get(user=current_user)
    watchlist_items = user_watchlist.listings.all()

    # Displays the listing's page
    return render(request, "auctions/listing.html",
                  {"title": item_name,
                   "listing": listing,
                   "watchlist": watchlist_items})


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
