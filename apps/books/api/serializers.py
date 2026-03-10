from rest_framework import serializers

from apps.books.models import Book, Genre, get_author_model


class BookAuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class BookSerializer(serializers.ModelSerializer):
    genre = serializers.CharField(
        max_length=50,
        source="genre.name",
        trim_whitespace=False,
        required=True
    )
    authors = BookAuthorSerializer(many=True, read_only=True)
    author_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=get_author_model().objects.only("id").all(),
        source="authors"
    )

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "summary",
            "isbn",
            "authors",
            "author_ids",
            "publication_date",
            "genre",
        )

    def validate(self, attrs):
        genre_name = attrs.pop("genre", None)
        if genre_name:
            attrs["genre"], _ = Genre.objects.get_or_create(name=genre_name)
        return attrs
