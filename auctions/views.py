from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.core.exceptions import ObjectDoesNotExist

from .models import User, Listing, Watchlist, Bid, Comment
from .forms import ListingForm, BidForm, CommentForm


# Default page (displays all the listings):
def index(request):
    active_listings = Listing.objects.filter(active=True)

    return render(request,
                  "auctions/index.html", {"listings": active_listings})


# View for each Individual listing:
def listing(request, item_id):
    if request.method == "GET":
        all_listings = Listing.objects.all()

        # Get listing and comments data
        try:
            listing = Listing.objects.get(pk=item_id)
            comments = Comment.objects.filter(item=listing)

        # 404
        except ObjectDoesNotExist:
            return render(request, "auctions/error_page.html",
                          {"error": "Listing not found."})

        # Check if user is authenticated
        try:
            user_id = request.user.id
            current_user = User.objects.get(pk=user_id)

        # If user is anonymous
        except ObjectDoesNotExist:
            return render(request, "auctions/listing.html",
                          {"listing": listing, "comments": comments,
                           "user": None, "all_listings": all_listings})

        # Watchlist data for current user
        user_watchlist = Watchlist.objects.get(user=current_user)
        watchlist_items = user_watchlist.listings.all()

        # Bid data
        try:
            current_bid = Bid.objects.get(listing=listing)

        except ObjectDoesNotExist:
            current_bid = None

        # Form fields
        form = BidForm()
        comment_form = CommentForm()

        return render(request, "auctions/listing.html",
                      {"user": current_user, "listing": listing,
                       "bid": current_bid, "watchlist": watchlist_items,
                       "form": form, "comment": comment_form,
                       "comments": comments, "all_listings": all_listings})

    # POST
    if request.method == "POST":

        user_id = request.user.id
        current_user = User.objects.get(pk=user_id)

        if "delete-comment" in request.POST:
            comment_pk = request.POST["comment-pk"]
            comment = Comment.objects.get(pk=comment_pk)
            if comment.author == current_user:
                comment.delete()
                item = comment.item
                return HttpResponseRedirect(reverse("listing", args=[item.pk]))

        return render(request, "auctions/error_page.html",
                      {"error": "Error."})


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
            if category == "":
                category = "Unspecified"

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


# View for bids' logic
@login_required(login_url="login")
def bidding(request):
    if request.method == "POST":

        # Get form data
        form = BidForm(request.POST)
        item_id = int(request.POST["listing"])

        # Get listing data
        listing = Listing.objects.get(pk=item_id)
        price = listing.starting_bid
        seller = listing.seller

        # Get current user data
        user_id = request.user.id
        user = User.objects.get(pk=user_id)

        # Form validation, and making sure a seller can't bid on own item
        if form.is_valid() and user != listing.seller:

            # Clean form data
            offer = form.cleaned_data["offer"]

            # Attempt to collect existing bid data
            try:
                latest_bid = Bid.objects.get(listing=listing)
                if latest_bid.is_open is False:
                    return render(request, "auctions/error_page.html",
                                  {"error": "Auction is closed."})

                latest_offer = latest_bid.offer
                offers_count = latest_bid.offer_count

                # Delete previous bid data if new offer is legit
                if int(offer) > latest_offer:
                    latest_bid.delete()

            # If no existing bid data exists:
            except ObjectDoesNotExist:
                latest_offer = 0
                offers_count = 0

            # Check if offer is legit on both counts
            if int(offer) >= price and int(offer) > latest_offer:

                count = offers_count + 1
                new_bid = Bid(listing=listing, seller=seller,
                              starting_bid=price, offer=offer,
                              bidder=user, offer_count=count)
                new_bid.save()

                # Redirect back to the listing's link
                return HttpResponseRedirect(reverse("listing", args=[item_id]))

            return render(request, "auctions/error_page.html",
                          {"error": "Bid is too low."})

    return render(request, "auctions/error_page.html",
                  {"error": "Invalid request."})


# View for closing/opening bids
@login_required(login_url="login")
def bid_status(request):
    if request.method == "POST":
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
                # As well as the corresponding active value in Listing
                if action == "Close Auction":
                    bid.is_open = False
                    listing.active = False

                elif action == "Open Auction":
                    bid.is_open = True
                    listing.active = True

                bid.save()
                listing.save()

            else:
                return render(request, "auctions/error_page.html",
                              {"error": "Error. Try again"})

            # Redirect back to the listing's page
            return HttpResponseRedirect(reverse("listing", args=[item_id]))

    return render(request, "auctions/error_page.html",
                  {"error_page": "Page not found"})


# View for listing all categories
def categories(request):

    listings = Listing.objects.all()
    categories_list = []

    for listing in listings:
        categories_list.append(listing.category)

    all_categories = set(categories_list)

    return render(request, "auctions/category_list.html",
                  {"categories": all_categories})


# View for each category
def category(request, category_name):
    group = Listing.objects.filter(category=category_name, active=True)

    return render(request, "auctions/category.html",
                  {"group": group,
                   "title": category_name})


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


# View for creating comments
def create_comments(request):
    if request.method == "POST":

        item_id = int(request.POST["listing"])
        listing = Listing.objects.get(pk=item_id)

        user_id = request.user.id
        current_user = User.objects.get(pk=user_id)

        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.cleaned_data["content"]

            new_comment = Comment(item=listing, content=comment,
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
