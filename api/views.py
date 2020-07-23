from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer

from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication

from accounts.models import PublicKeys


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
