from django.contrib import admin

from .models import Book, Genre, UserFavoriteBook


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("id", "name")
    list_per_page = 20


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    autocomplete_fields = ("genre", "authors")
    list_select_related = ("genre",)
    list_display = ("id", "title", "isbn", "publication_date", "genre")
    list_filter = ("publication_date",)
    search_fields = ("isbn", "title", "author__last_name")
    list_per_page = 20


@admin.register(UserFavoriteBook)
class UserFavoriteBookAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user", "book")
    list_select_related = ("user", "book")
    list_display = ("id", "user", "book", "added_at")
    list_filter = ("added_at",)
    search_fields = ("book__id", "book__title", "user__id", "user__email")
    list_per_page = 20
