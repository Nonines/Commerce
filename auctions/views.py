from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.core.exceptions import ObjectDoesNotExist

from .models import User, Listing, Watchlist, Bid
from .forms import ListingForm, BidForm


# Default page (displays all the listings):
def index(request):
    # When this view is called, retrieve all objects(data in database fields)
    # from the Listing table by constructing a QuerySet, and passing it as
    # context to the rendered template
    listings = Listing.objects.all()

    return render(request,
                  "auctions/index.html", {"listings": listings})


# View for each Individual listing:
def listing(request, item_id):

    # Gets the current user id and Gets the current user
    user_id = request.user.id
    current_user = User.objects.get(pk=user_id)
    # Gets the items in the user's watchlist
    user_watchlist = Watchlist.objects.get(user=current_user)
    watchlist_items = user_watchlist.listings.all()
    # Gets the item object
    listing = Listing.objects.get(pk=item_id)

    # If this is a POST request:
    if request.method == "POST":

        # Get the form data
        form = BidForm(request.POST)

        # Check if the form instance is valid
        if form.is_valid():

            # Get the first bid
            offer = form.cleaned_data["offer"]

            # And the other parameters for the bid instance
            price = listing.starting_bid   # starting bid
            seller_id = listing.seller.id  # item's seller

            # Check if this is the first bid request
            try:
                current_bid = Bid.objects.get(listing=listing)

            except ObjectDoesNotExist:
                # If it's the first, create a record of the bid in the database
                # The first bid must at least, equal the starting bid
                if int(offer) >= int(price):

                    new_bid = Bid(listing=listing, seller_id=seller_id,
                                  starting_bid=price, offer=offer,
                                  bidder=current_user, offer_count=1)
                    new_bid.save()
                    message = "Bid successful!"
                else:
                    new_bid = current_bid
                    message = "Your bid is too low!"

            else:
                # If (a) prior bid(s) exist(s):
                # Retrive the data to be used as kwargs
                previous_offer = current_bid.offer  # Latest bid in database
                count = current_bid.offer_count + 1  # Total Number of bids

                # Check if the new offer is valid
                if offer > previous_offer:

                    new_bid = Bid(listing=listing, seller_id=seller_id,
                                  starting_bid=price, offer=offer,
                                  bidder=current_user, offer_count=count)

                    # Delete the previous offer from record
                    current_bid.delete()

                    new_bid.save()
                    message = "Bid successful!"
                else:
                    new_bid = current_bid
                    message = "Your bid is too low!"

            finally:
                # And display the page, with an error if the bid is too low
                return render(request, "auctions/listing.html",
                              {"user": current_user,
                               "listing": listing, "bid": new_bid,
                               "watchlist": watchlist_items,
                               "message": message, "form": form})

        # If the form fails validation, return an error:
        else:
            message = "Invalid input"
            return render(request, "auctions/listing.html",
                          {"user": current_user,
                           "listing": listing, "bid": current_bid,
                           "watchlist": watchlist_items,
                           "message": message, "form": form})

    # If it is a GET request:
    else:
        try:
            current_bid = Bid.objects.get(listing=listing)

        except ObjectDoesNotExist:
            pass

        form = BidForm
        # Displays the listing's page
        return render(request, "auctions/listing.html",
                      {"user": current_user,
                       "listing": listing,
                       "bid": current_bid,
                       "watchlist": watchlist_items,
                       "form": form})


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

    # Get the currently logged-in user
    user_id = request.user.id
    current_user = User.objects.get(pk=user_id)

    # get the current user's watchlist
    user_watchlist = Watchlist.objects.get(user=current_user)

    # If it is a post request:
    if request.method == "POST":

        # Collect data from the post, including the item being added
        form = request.POST
        item_id = form["item_id"]
        current_item = Listing.objects.get(pk=item_id)

        # Determine which action is being performed
        if form["state"] == "Add":
            user_watchlist.listings.add(current_item)
        elif form["state"] == "Remove":
            user_watchlist.listings.remove(current_item)

        # Refresh the current Listing's page
        return HttpResponseRedirect(reverse("listing", args=[current_item.pk]))

    # If it's a get request, display the Watchlist page
    watchlist_items = user_watchlist.listings.all()
    return render(request, "auctions/watchlist.html",
                  {"watchlist": watchlist_items})


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

        # Create a Watchlist field in the database for every new user
        try:
            Watchlist.objects.create(user=user)
        except IntegrityError:
            print("Integrity error")

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
