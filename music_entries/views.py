from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models.functions import Lower

from .models import MusicEntry
from accounts.models import PublicKeys

from .forms import MusicEntryForm, LinkEntryForm, SearchQueryForm, MusicEntryEditForm

from .spotify_parser import SpotifyParser

from django.core import serializers

import json

def default(request):
    return render(request, "base_layout.html")

# Create MusicEntryList that will be shown to the user
def MusicEntryListCreate(request, key):
    # Query as per passed arguments in request
    queryset = MusicEntry.objects.all().filter(public_key__exact=key)
    if request.GET.get("title"):
        queryset = queryset.filter(title__icontains=request.GET.get("title"))
    if request.GET.get("artist"):
        queryset = queryset.filter(artist__icontains=request.GET.get("artist"))
    if request.GET.get("genre"):
        queryset = queryset.filter(genre__icontains=request.GET.get("genre"))
    if request.GET.get("type") != "any":
        queryset = queryset.filter(type__icontains=request.GET.get("type"))

    # Order if requested
    if request.GET.get("order_by"):
        order = request.GET.get("order_by")
        if order[0] == "-":
            # Reverse order
            queryset = queryset.order_by(Lower(order[1:])).reverse()
        else:
            # Normal order
            queryset = queryset.order_by(Lower(request.GET.get("order_by")))

    # Serialize and return
    mes = serializers.serialize("json", queryset)
    return JsonResponse(json.loads(mes), content_type="application/json", safe=False)


# Submit music entry
def submit(request):
    if request.method == "POST":
        form = MusicEntryForm(request.POST)
        if form.is_valid():
            # Get user's public key
            key = (
                PublicKeys.objects.all().get(user_id__exact=request.user.id).public_key
            )

            # Create new music entry
            music_entry = MusicEntry()
            music_entry.title = form.cleaned_data["title"]
            music_entry.artist = form.cleaned_data["artist"]
            music_entry.genre = form.cleaned_data["genre"]
            music_entry.type = form.cleaned_data["type"]

            # Get link or "null" if not valid
            if len(form.cleaned_data["link"]) > 5:
                music_entry.link = form.cleaned_data["link"]
            else:
                music_entry.link = "null"

            # Set submitter and submitter's public_key
            music_entry.public_key = key
            music_entry.submitter = request.user.username
            music_entry.save()
            return redirect("/music/collection/")
        else:
            return render(request, "music_entries/music_submitter.html", {"form": form})
    else:
        # Create normal music entry form
        form = MusicEntryForm()

        # Create form for parsing (spotify) link
        form2 = LinkEntryForm()

        return render(
            request,
            "music_entries/music_submitter.html",
            {"form": form, "form2": form2},
        )


# Submit entry from link
def submit_link(request):
    if request.method == "POST":
        # Get form
        form2 = LinkEntryForm(request.POST)
        if form2.is_valid():
            # Create parser
            parser = SpotifyParser()
            # Parse link
            spotify_entry = parser.parse(form2.cleaned_data["link"])
            # If entry is None, show error
            if spotify_entry is None:
                return render(request, "music_entries/spotify_error.html")

            # Create MusicEntryForm to be passed forward
            music_entry_form = MusicEntryForm()
            # Fill data from parsed entry
            music_entry_form.fields["title"].initial = spotify_entry.title
            music_entry_form.fields["artist"].initial = spotify_entry.artist
            music_entry_form.fields["genre"].initial = spotify_entry.genre
            music_entry_form.fields["type"].initial = spotify_entry.type
            music_entry_form.fields["link"].initial = spotify_entry.link
            # Pass data to submitter
            return render(request, "music_entries/music_submitter.html", {"form": music_entry_form})

    # If not POST or something went wrong, show empty forms
    music_entry_form = MusicEntryForm()
    form2 = LinkEntryForm()
    return render(
        request, "music_entries/music_submitter.html", {"form": music_entry_form, "form2": form2}
    )



# Show collection
def view(request, key):
    # Get all entries
    mes = MusicEntry.objects.all().filter(public_key__exact=key)

    # Get query form
    search_form = SearchQueryForm()
    focus_set = False # Whether we already set focus

    # Ordering
    if request.GET.get("order_by"):
        order = request.GET.get("order_by")
        if order[0] == "-":
            # Reverse order
            mes = mes.order_by(Lower(order[1:])).reverse()
        else:
            # Normal order
            mes = mes.order_by(Lower(request.GET.get("order_by")))
    # Query title
    if request.GET.get("title"):
        search_form.fields["title"].initial = request.GET.get("title")
        mes = mes.filter(title__icontains=request.GET.get("title"))
        if not focus_set:
            search_form.fields["title"].widget.attrs.update({"autofocus": "autofocus"})
            focus_set = True
    # Query artist
    if request.GET.get("artist"):
        search_form.fields["artist"].initial = request.GET.get("artist")
        mes = mes.filter(artist__icontains=request.GET.get("artist"))
        if not focus_set:
            search_form.fields["artist"].widget.attrs.update({"autofocus": "autofocus"})
            focus_set = True
    # Query genre
    if request.GET.get("genre"):
        search_form.fields["genre"].initial = request.GET.get("genre")
        mes = mes.filter(genre__icontains=request.GET.get("genre"))
        if not focus_set:
            search_form.fields["genre"].widget.attrs.update({"autofocus": "autofocus"})
            focus_set = True
    # Query type
    if request.GET.get("type"):
        search_form.fields["type"].initial = request.GET.get("type")
        if request.GET.get("type") != "any":
            mes = mes.filter(type__icontains=request.GET.get("type"))

    # Set focus on title if not already set
    if not focus_set:
        search_form.fields["title"].widget.attrs.update({"autofocus": "autofocus"})
        focus_set = True

    # Render the collection
    return render(
        request,
        "music_entries/music_viewer.html",
        {"music_entries": mes, "form": search_form},
    )


# For viewing your own collection
def view_own(request):
    if request.user.is_authenticated:
        # Get user's public key
        key = PublicKeys.objects.all().get(user_id__exact=request.user.id).public_key
        # Redirect to this user's collectoin
        return redirect("/music/collection/" + key)
    else:
        # Redirect home if not logged in
        return redirect("home")


# For editing entries
def edit(request, entry_id):
    if not request.user.is_authenticated:
        # Redirect home if not logged in
        redirect("home")

    # Get user's public key
    key = PublicKeys.objects.all().get(user_id__exact=request.user.id).public_key
    try:
        # Try to get that entry
        entry = MusicEntry.objects.all().get(id__exact=entry_id)
    except:
        # TODO: tell user its wrong id
        return redirect("view-own")

    if request.method == "POST":
        form = MusicEntryEditForm(request.POST, instance=entry)
        if form.is_valid():
            # Update entry
            entry.title = form.cleaned_data["title"]
            entry.artist = form.cleaned_data["artist"]
            entry.genre = form.cleaned_data["genre"]
            entry.type = form.cleaned_data["type"]
            entry.link = form.cleaned_data["link"]
            entry.save()

        return redirect("view-own")

    if entry.public_key == key:
        # Render filled form so user can edit
        form = MusicEntryEditForm(instance=entry)
        return render(
            request,
            "music_entries/music_edit.html",
            {"form": form, "entry_id": entry_id},
        )
    else:
        # TODO: tell user it's not his entry
        return redirect("view-own")
