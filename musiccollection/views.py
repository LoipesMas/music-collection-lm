from django.shortcuts import render


def about(request):
    return render(request, "about.html")


def home(request):
    return render(request, "home.html")


def mirror(request):
    return render(request, "test.html")
