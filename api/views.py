from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    TokenAuthentication,
    SessionAuthentication,
    BasicAuthentication,
)

from accounts.models import PublicKeys

from music_entries.forms import MusicEntryForm
from music_entries.models import MusicEntry

from music_entries.spotify_parser import SpotifyParser


class UserInfoView(APIView):
    authentication_classes = [
        TokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    ]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            public_key = (
                PublicKeys.objects.all().get(user_id__exact=request.user.id).public_key
            )
            content = {
                "user": request.user.username,
                "public_key": public_key,  # None
            }
            return Response(content)
        else:
            content = {"message": "Not authenticated"}
            return Response(content)


class MusicSubmit(APIView):
    authentication_classes = [
        TokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    ]
    permission_classes = [IsAuthenticated]

    # Creating new music entry
    def post(self, request):
        if request.method == "POST":
            form = MusicEntryForm(request.POST)
            if form.is_valid():
                # Get user public key
                key = (
                    PublicKeys.objects.all()
                    .get(user_id__exact=request.user.id)
                    .public_key
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

                return Response("OK")

            response = Response("Form data invalid")
            response.status_code = 400
            return response


class ParseView(APIView):

    authentication_classes = [
        TokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    ]
    permission_classes = [IsAuthenticated]

    # Parsing spotify submition into music entry form
    def post(self, request):
        url = request.POST.get("url")
        parser = SpotifyParser()

        # Try to parse the url
        spotify_entry = parser.parse(url)
        if spotify_entry is None:
            response = Response("Url invalid")
            response.status_code = 400
        else:
            # Create form and return it
            data = {}
            data["title"] = spotify_entry.title
            data["artist"] = spotify_entry.artist
            data["genre"] = spotify_entry.genre
            data["type"] = spotify_entry._type
            data["link"] = spotify_entry.link
            return Response(data)
        return Response()
