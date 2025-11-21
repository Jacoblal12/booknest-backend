from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# ------------------------------------------------------------
# BOOK MODEL
# ------------------------------------------------------------
class Book(models.Model):
    AVAILABLE_CHOICES = [
        ('rent', 'Rent'),
        ('exchange', 'Exchange'),
        ('donate', 'Donate'),
    ]

    owner = models.ForeignKey(User, related_name="books", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    cover = models.ImageField(upload_to="book_covers/", null=True, blank=True)

    # NOW matches BookRequest request types
    available_for = models.CharField(max_length=20, choices=AVAILABLE_CHOICES)

    # Optional GPS fields (future feature)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} — {self.owner.username}"


# ------------------------------------------------------------
# BOOK REQUEST MODEL
# ------------------------------------------------------------
class BookRequest(models.Model):
    REQUEST_TYPES = [
        ('rent', 'Rent'),
        ('exchange', 'Exchange'),
        ('donate', 'Donate'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="requests")
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="book_requests")

    # NOW perfectly aligned with Book.available_for
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)

    message = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.requester.username} → {self.book.title} ({self.request_type})"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('rent', 'Rent'),
        ('exchange', 'Exchange'),
        ('donate', 'Donate'),
    ]

    STATUS_CHOICES = [
        ('received', 'Received'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="transactions")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_transactions")
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_transactions")

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.book.title} — {self.transaction_type} ({self.status})"
