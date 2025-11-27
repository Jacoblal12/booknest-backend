from rest_framework import serializers
from django.db.models import Avg, Count
from .models import Announcement, Book, BookRequest, Feedback, Notification, Report, Transaction, Wishlist

class BookSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    avg_rating = serializers.SerializerMethodField()
    request_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'owner', 'title', 'author', 'description', 'isbn', 'cover',
            'available_for', 'location_lat', 'location_lng',
            'created_at', 'updated_at',
            'avg_rating', 'request_count'
        ]
        read_only_fields = ['owner', 'avg_rating', 'request_count']

    # --- computed fields ---
    def get_avg_rating(self, obj):
        # Use annotation if available (more efficient)
        if hasattr(obj, "avg_rating"):
            return round(obj.avg_rating or 0, 2)

        agg = obj.feedbacks.aggregate(avg=Avg("rating"))
        return round(agg["avg"] or 0, 2)

    def get_request_count(self, obj):
        if hasattr(obj, "request_count"):
            return obj.request_count
        return obj.requests.count()

class BookRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookRequest
        fields = "__all__"
        read_only_fields = ["requester", "status"]

    def validate(self, data):
        user = self.context['request'].user
        book = data['book']
        req_type = data.get("request_type")
        exchange_book = data.get("exchange_book")

        # 1. Prevent requesting your own book
        if book.owner == user:
            raise serializers.ValidationError(
                {"error": "You cannot request your own book."}
            )

        # 2. Prevent mixed request types
        if book.available_for != req_type:
            raise serializers.ValidationError(
                {"error": f"This book is only available for: {book.available_for}."}
            )

        # 3. Prevent duplicate PENDING requests
        existing = BookRequest.objects.filter(
            book=book,
            requester=user,
            status="pending"
        ).exists()

        if existing:
            raise serializers.ValidationError(
                {"error": "You already have a pending request for this book."}
            )

        # 4. Exchange-specific validation
        if req_type == "exchange":
            if exchange_book is None:
                raise serializers.ValidationError(
                    {"exchange_book": "You must provide a book to exchange."}
                )

            if exchange_book.owner != user:
                raise serializers.ValidationError(
                    {"exchange_book": "You can only offer books that you own."}
                )

            if exchange_book == book:
                raise serializers.ValidationError(
                    {"exchange_book": "You cannot exchange a book with itself."}
                )

        return data

    def create(self, validated_data):
        validated_data['requester'] = self.context['request'].user
        return super().create(validated_data)



class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ["owner", "transaction_type", "book", "start_date"]

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = "__all__"
        read_only_fields = ['user']

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"
        read_only_fields = ['user']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ['reporter', 'status', 'admin_remarks']

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = "__all__"
        read_only_fields = ['created_by']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ["user", "created_at"]
