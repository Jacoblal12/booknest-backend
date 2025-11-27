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

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="wishlist_users")
    
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')  # prevents duplicates

    def __str__(self):
        return f"{self.user.username} → {self.book.title}"

class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedbacks")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="feedbacks")

    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'book')  # A user gives only 1 review per book

    def __str__(self):
        return f"{self.user.username} → {self.book.title} ({self.rating}★)"

class Report(models.Model):
    REPORT_TYPES = [
        ('book', 'Book'),
        ('user', 'User'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    ]

    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)

    reported_book = models.ForeignKey(
        Book, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports"
    )

    reported_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reported_against"
    )

    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reports_made"
    )

    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    admin_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.reported_book.title if self.reported_book else self.reported_user.username
        return f"Report on {target} ({self.status})"

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="announcements")
    
    is_active = models.BooleanField(default=True)  # admins can toggle visibility

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.user.username}: {self.message}"
