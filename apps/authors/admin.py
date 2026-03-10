from django.contrib import admin

from .models import Author


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ("id", "first_name", "last_name")
    list_display = ("id", "first_name", "last_name", "date_of_birth", "date_of_death")
    list_filter = ("date_of_birth", "date_of_death")
    list_per_page = 20
