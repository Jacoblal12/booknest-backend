from rest_framework import serializers
from .models import Book, Transaction

class BookSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ("id", "owner", "created_at", "updated_at")

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ["owner", "transaction_type", "book", "start_date"]
