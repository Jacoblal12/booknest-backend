from django_filters import rest_framework as filters
from .models import Book

class BookFilter(filters.FilterSet):
    class Meta:
        model = Book
        # Exclude the JSON field that caused the error
        exclude = ['available_for']
