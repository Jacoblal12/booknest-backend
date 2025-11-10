from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Book(models.Model):
    owner = models.ForeignKey(User, related_name="books", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    cover = models.ImageField(upload_to="book_covers/", null=True, blank=True)
    available_for = models.JSONField(default=dict)  # e.g. {"borrow": True, "exchange": False, "donate": False}
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} — {self.owner}"
