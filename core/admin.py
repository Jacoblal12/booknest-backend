from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Announcement, Book, Feedback, Report, Transaction, Wishlist

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'owner', 'created_at')
    search_fields = ('title', 'author',)
    list_filter = ('created_at',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_type', 'reporter', 'status', 'created_at')
    list_filter = ('status', 'report_type')
    search_fields = ('reason',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'message')

admin.site.register(Transaction)

admin.site.register(Wishlist)

admin.site.register(Feedback)