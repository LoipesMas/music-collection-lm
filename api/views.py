from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer

from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication

from accounts.models import PublicKeys

from music_entries.forms import MusicEntryForm
from music_entries.models import MusicEntry

from music_entries.spotify_parser import SpotifyParser, SpotifyMusicEntry

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserInfoView(APIView):
    authentication_classes = [TokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            public_key = PublicKeys.objects.all().get(
                user_id__exact=request.user.id).public_key
            content = {
                'user': request.user.username,
                'public_key': public_key,  # None
            }
            return Response(content)
        else:
            content = {
                'message': 'Not authenticated'
            }
            return Response(content)


class MusicSubmit(APIView):
    authentication_classes = [TokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.method == "POST":
            form = MusicEntryForm(request.POST)
            if form.is_valid():
                key = PublicKeys.objects.all().get(user_id__exact=request.user.id).public_key

                me = MusicEntry()
                me.title = form.cleaned_data['title']
                me.artist = form.cleaned_data['artist']
                me.genre = form.cleaned_data['genre']
                me.type = form.cleaned_data['type']
                if len(form.cleaned_data['link']) > 5:
                    me.link = form.cleaned_data['link']
                else:
                    me.link = 'null'

                me.public_key = key
                me.submitter = request.user.username
                me.save()

                return Response("OK")

            response = Response("Form data invalid")
            response.status_code = 400
            return response


class ParseView(APIView):

    authentication_classes = [TokenAuthentication,
                              SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        url = request.POST.get("url")
        parser = SpotifyParser()
        spotify_entry = parser.parse(url)
        if spotify_entry is None:
            response = Response("Url invalid")
            response.status_code = 400
        else:
            data = {}
            data['title'] = spotify_entry.title
            data['artist'] = spotify_entry.artist
            data['genre'] = spotify_entry.genre
            data['type'] = spotify_entry._type
            data['link'] = spotify_entry.link
            return Response(data)
        return Response()
