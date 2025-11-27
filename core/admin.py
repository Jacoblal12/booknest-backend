from django.contrib import admin
from .models import (
    Announcement, Book, BookRequest, Feedback, Report, Transaction, Wishlist
)

# -------------------------
# Book Admin
# -------------------------
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "available_for", "created_at")
    search_fields = ("title", "author", "isbn")
    list_filter = ("available_for", "created_at")


# -------------------------
# Book Request Admin
# -------------------------
@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ("book", "requester", "request_type", "exchange_book", "status", "created_at")
    list_filter = ("request_type", "status", "created_at")
    search_fields = ("book__title", "requester__username", "exchange_book__title")



# -------------------------
# Transaction Admin
# -------------------------
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("book", "owner", "borrower", "transaction_type", "status", "created_at")
    list_filter = ("transaction_type", "status", "created_at")


# -------------------------
# Wishlist Admin
# -------------------------
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "added_at")
    list_filter = ("added_at",)


# -------------------------
# Feedback Admin
# -------------------------
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("comment",)


# -------------------------
# Report Admin
# -------------------------
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_type', 'reporter', 'status', 'created_at')
    list_filter = ('status', 'report_type')
    search_fields = ('reason',)


# -------------------------
# Announcement Admin
# -------------------------
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'message')