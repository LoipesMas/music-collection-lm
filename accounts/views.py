from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout

from .models import PublicKeys

import random
import string

def signup_view(request):
    if request.method == "POST":
        # Get form from request
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Logn the new user
            user = form.save()
            login(request, user)

            public_key_entry = PublicKeys()

            # current public keys
            keys = [x.public_key for x in PublicKeys.objects.all()]

            # create new one until it's unqiue
            # there's 208 bilions combinations, but better safe than sorry
            while True:
                # generate 8 random lower case letters for a public key (the one you share)
                key = "".join(random.choice(string.ascii_lowercase) for _ in range(8))
                if not key in keys:
                    break

            # Create and save new public key entry
            public_key_entry.public_key = key
            public_key_entry.user_id = request.user.id
            public_key_entry.save()

            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")

    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")
