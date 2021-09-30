from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models.functions import Lower

from .models import MusicEntry
from accounts.models import PublicKeys

from .forms import MusicEntryForm, LinkEntryForm, SearchQueryForm, MusicEntryEditForm

from .spotify_parser import SpotifyParser, SpotifyMusicEntry
from django.core.validators import URLValidator

import logging

from django.core import serializers

import json

# Create your views here.


def default(request):
    return render(request, "base_layout.html")


def MusicEntryListCreate(request, key):
    queryset = MusicEntry.objects.all().filter(public_key__exact=key)
    if request.GET.get("title"):
        queryset = queryset.filter(title__icontains=request.GET.get("title"))
    if request.GET.get("artist"):
        queryset = queryset.filter(artist__icontains=request.GET.get("artist"))
    if request.GET.get("genre"):
        queryset = queryset.filter(genre__icontains=request.GET.get("genre"))
    if request.GET.get("type") != "any":
        queryset = queryset.filter(type__icontains=request.GET.get("type"))

    if request.GET.get("order_by"):
        order = request.GET.get("order_by")
        if order[0] == "-":
            queryset = queryset.order_by(Lower(order[1:])).reverse()
        else:
            queryset = queryset.order_by(Lower(request.GET.get("order_by")))

    mes = serializers.serialize("json", queryset)
    return JsonResponse(json.loads(mes), content_type="application/json", safe=False)


def submit(request):
    if request.method == "POST":
        form = MusicEntryForm(request.POST)
        if form.is_valid():
            key = (
                PublicKeys.objects.all().get(user_id__exact=request.user.id).public_key
            )

            me = MusicEntry()
            me.title = form.cleaned_data["title"]
            me.artist = form.cleaned_data["artist"]
            me.genre = form.cleaned_data["genre"]
            me.type = form.cleaned_data["type"]
            if len(form.cleaned_data["link"]) > 5:
                me.link = form.cleaned_data["link"]
            else:
                me.link = "null"
            me.public_key = key
            me.submitter = request.user.username
            me.save()
            return redirect("/music/collection/")
        else:
            return render(request, "music_entries/music_submitter.html", {"form": form})
    else:
        form = MusicEntryForm()
        form2 = LinkEntryForm()
        return render(
            request,
            "music_entries/music_submitter.html",
            {"form": form, "form2": form2},
        )


def submit_link(request):
    if request.method == "POST":
        form2 = LinkEntryForm(request.POST)
        if form2.is_valid():
            key = (
                PublicKeys.objects.all().get(user_id__exact=request.user.id).public_key
            )
            mef = MusicEntryForm()
            parser = SpotifyParser()
            spotify_entry = parser.parse(form2.cleaned_data["link"])
            if spotify_entry is None:
                return render(request, "music_entries/spotify_error.html")
            mef.fields["title"].initial = spotify_entry.title
            mef.fields["artist"].initial = spotify_entry.artist
            mef.fields["genre"].initial = spotify_entry.genre
            mef.fields["type"].initial = spotify_entry._type
            mef.fields["link"].initial = spotify_entry.link
            return render(request, "music_entries/music_submitter.html", {"form": mef})
    else:
        mef = MusicEntryForm()
        form2 = LinkEntryForm()
    return render(
        request, "music_entries/music_submitter.html", {"form": mef, "form2": form2}
    )


def view(request, key):
    mes = MusicEntry.objects.all().filter(public_key__exact=key)
    search_form = SearchQueryForm()
    focus_set = False
    if request.GET.get("order_by"):
        order = request.GET.get("order_by")
        if order[0] == "-":
            mes = mes.order_by(Lower(order[1:])).reverse()
        else:
            mes = mes.order_by(Lower(request.GET.get("order_by")))
    if request.GET.get("title"):
        search_form.fields["title"].initial = request.GET.get("title")
        mes = mes.filter(title__icontains=request.GET.get("title"))
        if not focus_set:
            search_form.fields["title"].widget.attrs.update({"autofocus": "autofocus"})
            focus_set = True
    if request.GET.get("artist"):
        search_form.fields["artist"].initial = request.GET.get("artist")
        mes = mes.filter(artist__icontains=request.GET.get("artist"))
        if not focus_set:
            search_form.fields["artist"].widget.attrs.update({"autofocus": "autofocus"})
            focus_set = True
    if request.GET.get("genre"):
        search_form.fields["genre"].initial = request.GET.get("genre")
        mes = mes.filter(genre__icontains=request.GET.get("genre"))
        if not focus_set:
            search_form.fields["genre"].widget.attrs.update({"autofocus": "autofocus"})
            focus_set = True
    if request.GET.get("type"):
        search_form.fields["type"].initial = request.GET.get("type")
        if request.GET.get("type") != "any":
            mes = mes.filter(type__icontains=request.GET.get("type"))
    if not focus_set:
        search_form.fields["title"].widget.attrs.update({"autofocus": "autofocus"})
        focus_set = True
    return render(
        request,
        "music_entries/music_viewer.html",
        {"music_entries": mes, "form": search_form},
    )


def view_own(request):
    if request.user.is_authenticated:
        key = PublicKeys.objects.all().get(user_id__exact=request.user.id).public_key
        return redirect("/music/collection/" + key)
    else:
        return redirect("home")


def edit(request, entry_id):
    if not request.user.is_authenticated:
        redirect("home")

    key = PublicKeys.objects.all().get(user_id__exact=request.user.id).public_key
    try:
        entry = MusicEntry.objects.all().get(id__exact=entry_id)
    except:
        # TODO: tell user its wrong id
        return redirect("view-own")

    if request.method == "POST":
        form = MusicEntryEditForm(request.POST, instance=entry)
        if form.is_valid():
            key = (
                PublicKeys.objects.all().get(user_id__exact=request.user.id).public_key
            )
            entry.title = form.cleaned_data["title"]
            entry.artist = form.cleaned_data["artist"]
            entry.genre = form.cleaned_data["genre"]
            entry.type = form.cleaned_data["type"]
            entry.link = form.cleaned_data["link"]
            entry.save()

        return redirect("view-own")

    if entry.public_key == key:
        form = MusicEntryEditForm(instance=entry)
        return render(
            request,
            "music_entries/music_edit.html",
            {"form": form, "entry_id": entry_id},
        )
    else:
        # TODO: tell user it's not his entry
        return redirect("view-own")
