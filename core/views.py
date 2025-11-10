from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Book
from .serializers import BookSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('-created_at')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    filterset_fields = ['owner__id']
    search_fields = ['title', 'author', 'isbn', 'description']
    ordering_fields = ['created_at', 'title']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
