from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db import models
from .models import Book
from .serializers import BookSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Book, BookRequest, Transaction
from .serializers import BookSerializer, TransactionSerializer

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

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Show transactions where the user is owner OR borrower
        return Transaction.objects.filter(
            models.Q(owner=user) | models.Q(borrower=user)
        )
