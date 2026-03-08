import json
import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import analyze_review_sentiments, get_request, post_review


logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    """Handle user login."""
    data = json.loads(request.body)

    username = data["userName"]
    password = data["password"]

    user = authenticate(username=username, password=password)

    response_data = {"userName": username}

    if user is not None:
        login(request, user)
        response_data = {"userName": username, "status": "Authenticated"}

    return JsonResponse(response_data)


def logout_request(request):
    """Handle user logout."""
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)


@csrf_exempt
def registration(request):
    """Handle user registration."""
    data = json.loads(request.body)

    username = data["userName"]
    password = data["password"]
    first_name = data["firstName"]
    last_name = data["lastName"]
    email = data["email"]

    username_exist = False

    try:
        User.objects.get(username=username)
        username_exist = True
    except User.DoesNotExist:
        logger.debug("%s is a new user", username)

    if not username_exist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
        )

        login(request, user)

        data = {
            "userName": username,
            "status": "Authenticated",
        }

        return JsonResponse(data)

    data = {
        "userName": username,
        "error": "Already Registered",
    }

    return JsonResponse(data)


def get_dealerships(request, state="All"):
    """Return dealerships list."""
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"

    dealerships = get_request(endpoint)

    return JsonResponse({
        "status": 200,
        "dealers": dealerships,
    })


def get_dealer_reviews(request, dealer_id):
    """Return reviews for a dealer."""
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"

        reviews = get_request(endpoint)

        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail["review"])
            review_detail["sentiment"] = response["sentiment"]

        return JsonResponse({
            "status": 200,
            "reviews": reviews,
        })

    return JsonResponse({
        "status": 400,
        "message": "Bad Request",
    })


def get_dealer_details(request, dealer_id):
    """Return dealer details."""
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"

        dealership = get_request(endpoint)

        return JsonResponse({
            "status": 200,
            "dealer": dealership,
        })

    return JsonResponse({
        "status": 400,
        "message": "Bad Request",
    })


def get_cars(request):
    """Return available car models."""
    count = CarMake.objects.count()

    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related("car_make")

    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name,
        })

    return JsonResponse({
        "CarModels": cars,
    })


def add_review(request):
    """Submit a dealer review."""
    if not request.user.is_anonymous:
        data = json.loads(request.body)

        try:
            post_review(data)

            return JsonResponse({
                "status": 200,
            })

        except Exception:
            return JsonResponse({
                "status": 401,
                "message": "Error in posting review",
            })

    return JsonResponse({
        "status": 403,
        "message": "Unauthorized",
    })
