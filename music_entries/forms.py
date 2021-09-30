from django import forms

from .models import MusicEntry

from django.forms import ModelForm


class MusicEntryForm(forms.Form):
    title = forms.CharField(label="Title", max_length=256)
    artist = forms.CharField(label="Artist", max_length=256)
    genre = forms.CharField(label="Genre", max_length=256)
    type = forms.ChoiceField(label="Type", choices=MusicEntry.type_choices)
    link = forms.URLField(label="Link", required=False)


class LinkEntryForm(forms.Form):
    link = forms.URLField(label="Spotify Link")


class SearchQueryForm(forms.Form):
    type_choices = (
        ("any", "Any"),
        ("album", "Album"),
        ("song", "Song"),
        ("mix", "Playlist/Mix"),
    )
    title = forms.CharField(label="Title", max_length=256, required=False)
    artist = forms.CharField(label="Artist", max_length=256, required=False)
    genre = forms.CharField(label="Genre", max_length=256, required=False)
    type = forms.ChoiceField(label="Type", choices=type_choices, required=False)


class MusicEntryEditForm(forms.ModelForm):
    class Meta:
        model = MusicEntry
        fields = ("title", "artist", "genre", "type", "link")
