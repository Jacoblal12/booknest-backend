from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ("id", "owner", "created_at", "updated_at")
