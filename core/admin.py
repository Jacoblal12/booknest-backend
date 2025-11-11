from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'owner', 'created_at')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('genre', 'created_at')
