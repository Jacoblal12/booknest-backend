from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db import models
from .models import Book, Feedback, Report, Wishlist
from .serializers import BookSerializer, FeedbackSerializer, ReportSerializer, WishlistSerializer
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

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all().order_by('-added_at')
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Only return the logged-in user's wishlist
        return Wishlist.objects.filter(user=self.request.user)

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by('-created_at')
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        book_id = self.request.query_params.get('book')
        if book_id:
            return Feedback.objects.filter(book=book_id).order_by('-created_at')
        return Feedback.objects.filter(user=self.request.user)

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    def get_queryset(self):
        user = self.request.user

        # Admin sees all reports
        if user.is_staff:
            return Report.objects.all()

        # Regular user sees only THEIR reports
        return Report.objects.filter(reporter=user)
