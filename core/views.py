from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from django.db import models
from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.postgres.search import TrigramSimilarity
from .models import Announcement, Book, Feedback, Report, Wishlist
from .serializers import AnnouncementSerializer, BookRequestSerializer, BookSerializer, FeedbackSerializer, ReportSerializer, WishlistSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
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

    # Filtering, searching, ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['owner__id', 'available_for', 'author']
    search_fields = ['title', 'author', 'isbn', 'description']
    ordering_fields = ['created_at', 'title', 'author']

    def get_queryset(self):
        return (
            Book.objects
            .select_related("owner")                          # FK
            .prefetch_related("feedbacks", "requests")        # reverse lookups
            .annotate(
                avg_rating=Avg("feedbacks__rating"),
                request_count=Count("requests")
            )
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # ---------------------------------------------------
    # Fuzzy Search Endpoint (Optional Advanced Search)
    # ---------------------------------------------------
    @action(detail=False, methods=['get'], url_path='fuzzy-search')
    def fuzzy_search(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({"detail": "Missing query parameter ?q="}, status=400)

        books = Book.objects.annotate(
            similarity=TrigramSimilarity('title', query) +
                        TrigramSimilarity('author', query) +
                        TrigramSimilarity('description', query)
        ).filter(similarity__gt=0.1).order_by('-similarity')

        page = self.paginate_queryset(books)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
    
    # ---------------------------------------------------
    # My books endpoint(for flutter interface)
    # ---------------------------------------------------
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='my')
    def my_books(self, request):
        user = request.user
        qs = Book.objects.filter(owner=user).order_by('-created_at')

        # Apply performance optimization
        qs = qs.select_related('owner').prefetch_related('feedbacks', 'requests')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
    
    # ---------------------------------------------------
    # My requests endpoint(for flutter interface)
    # ---------------------------------------------------
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='my')
    def my_requests(self, request):
        user = request.user

        qs = BookRequest.objects.filter(
            models.Q(requester=user) |
            models.Q(book__owner=user)
        ).select_related('book', 'requester', 'book__owner').order_by('-created_at')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = BookRequestSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BookRequestSerializer(qs, many=True)
        return Response(serializer.data)

class BookRequestViewSet(viewsets.ModelViewSet):
    ...
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='my')
    def my_requests(self, request):
        user = request.user

        qs = BookRequest.objects.filter(
            models.Q(requester=user) |
            models.Q(book__owner=user)
        ).select_related('book', 'requester', 'book__owner').order_by('-created_at')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = BookRequestSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BookRequestSerializer(qs, many=True)
        return Response(serializer.data)

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
    
    # ---------------------------------------------------
    # My transactions endpoint(for flutter interface)
    # ---------------------------------------------------
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='my')
    def my_transactions(self, request):
        user = request.user

        qs = Transaction.objects.filter(
            models.Q(owner=user) |
            models.Q(borrower=user)
        ).select_related('book', 'owner', 'borrower').order_by('-created_at')

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TransactionSerializer(qs, many=True)
        return Response(serializer.data)

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

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        # admins can CRUD, users can only read
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
