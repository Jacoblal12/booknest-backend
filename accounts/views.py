from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from .models import Profile
from rest_framework import status
from .serializers import ProfileSerializer
from rest_framework.response import Response
from django.contrib.auth.models import User

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

@api_view(["POST"])
@permission_classes([AllowAny])   # PUBLIC ENDPOINT
def register_user(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")

    if not username or not password:
        return Response({"error": "Username & password required"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken"}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email)
    user.save()

    return Response({"message": "User created successfully"}, status=201)