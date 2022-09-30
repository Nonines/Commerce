from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from django.core.exceptions import ObjectDoesNotExist

from .models import User, Listing, Watchlist, Bid, Comment
from .forms import ListingForm, BidForm, CommentForm


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

    listing = Listing.objects.get(pk=item_id)

    # If it is a GET request:
    try:
        user_id = request.user.id
        current_user = User.objects.get(pk=user_id)

        user_watchlist = Watchlist.objects.get(user=current_user)
        watchlist_items = user_watchlist.listings.all()

        comments = Comment.objects.filter(item=listing)

    # Displays only basic info when user isn't logged in
    except (ObjectDoesNotExist, UnboundLocalError):
        return render(request, "auctions/listing.html",
                      {"listing": listing,
                       "user": None})

    form = BidForm()
    comment_form = CommentForm()
    try:
        current_bid = Bid.objects.get(listing=listing)

    # No bid info is rendered when there aren't any bids yet
    except ObjectDoesNotExist:
        return render(request, "auctions/listing.html",
                      {"user": current_user, "listing": listing,
                       "watchlist": watchlist_items, "form": form,
                       "comment": comment_form, "comments": comments})

    # If user is logged in and there are ongoing bids:
    return render(request, "auctions/listing.html",
                  {"user": current_user, "listing": listing,
                   "bid": current_bid, "watchlist": watchlist_items,
                   "form": form, "comment": comment_form,
                   "comments": comments})


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


# @login_required(login_url="login")
def bidding(request):
    if "new_bid" in request.POST:

        # Get form data
        form = BidForm(request.POST)
        item_id = int(request.POST["listing"])

        # Get listing data
        listing = Listing.objects.get(pk=item_id)

        # Get current user data
        user_id = request.user.id
        user = User.objects.get(pk=user_id)

        # Form validation, and making sure a seller can't bid on own item
        if form.is_valid() and user != listing.seller:

            # Clean form data and get necessary listing data
            offer = form.cleaned_data["offer"]
            price = listing.starting_bid
            seller = listing.seller

            # Attempt to collect existing bid data
            try:
                current_bid = Bid.objects.get(listing=listing)

            # Except block runs when there's no existing bid
            except ObjectDoesNotExist:

                # First offer should be at least equal to starting_bid
                if int(offer) >= int(price):

                    # Create a new bid and save it to the database
                    new_bid = Bid(listing=listing, seller=seller,
                                  starting_bid=price, offer=offer,
                                  bidder=user, offer_count=1)
                    new_bid.save()
                else:
                    return HttpResponse("Bid is too low.")

            # Else block runs when a bid already exists
            else:
                # Update existing bid with new offer and bidder data
                count = current_bid.offer_count + 1

                # New offers must be higher than previous ones
                if offer > current_bid.offer:

                    # Check whether auction is open/close
                    status = current_bid.is_open

                    # If it's closed, return an error message
                    if status is False:
                        return HttpResponse("This auction is closed.")

                    # If it's open, create a new bid instance
                    new_bid = Bid(listing=listing, seller=seller,
                                  starting_bid=price, offer=offer,
                                  bidder=user, offer_count=count)

                    # Deleting the previous bid, save the latest
                    current_bid.delete()
                    new_bid.save()
                else:
                    return HttpResponse("Bid is too low.")

            # Redirect back to the listing's link
            return HttpResponseRedirect(reverse("listing", args=[item_id]))

        # Prevents malicious users from tampering with form data
        else:
            return HttpResponse("Can't bid on own item.")


def bid_status(request):
    if "status" in request.POST:

        # Get request data
        item_id = int(request.POST["listing"])
        action = request.POST["status"]

        # Get listing data
        listing = Listing.objects.get(pk=item_id)

        # Get current user data
        user_id = request.user.id
        user = User.objects.get(pk=user_id)

        # Checks if user has access to the listing
        if user == listing.seller:

            # Get the bid data for the listing
            bid = Bid.objects.get(listing=listing)

            # Change the is_open field's value as required
            if action == "Close Auction":
                bid.is_open = False

            elif action == "Open Auction":
                bid.is_open = True

            bid.save()

        else:
            return HttpResponse("Error.")

        # Redirect back to the listing's page
        return HttpResponseRedirect(reverse("listing", args=[item_id]))


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


def comments(request):
    if request.method == "POST":

        item_id = int(request.POST["listing"])
        listing = Listing.objects.get(pk=item_id)

        user_id = request.user.id
        current_user = User.objects.get(pk=user_id)

        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.cleaned_data["comment"]

            new_comment = Comment(item=listing, comment=comment,
                                  author=current_user)

            new_comment.save()

        return HttpResponseRedirect(reverse("listing", args=[item_id]))


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
