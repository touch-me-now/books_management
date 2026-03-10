import django_filters
from django.db.models import Q

from apps.books.models import Book, Genre, get_author_model


class BookFilter(django_filters.FilterSet):
    authors = django_filters.ModelMultipleChoiceFilter(
        queryset=get_author_model().objects.all(),
        field_name="authors",
    )
    genres = django_filters.ModelMultipleChoiceFilter(
        queryset=Genre.objects.all(),
        field_name="genre",
    )
    publication_date = django_filters.DateFromToRangeFilter(
        field_name="publication_date",
    )
    search = django_filters.CharFilter(method="filter_search")
    ordering = django_filters.OrderingFilter(
        fields=(
            ("publication_date", "publication_date"),
            ("genre__name", "genre"),
            ("authors__last_name", "author"),
        )
    )
    favorite = django_filters.BooleanFilter(method="filter_favorites")

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(authors__last_name__icontains=value)
        ).distinct()  # distinct importand for M2M

    def filter_favorites(self, queryset, name, value):
        method = "filter" if value is True else "exclude"
        return getattr(queryset, method)(user_favorites__user=self.request.user)

    class Meta:
        model = Book
        fields = ("authors", "genres", "publication_date", "search", "ordering", "favorite")
