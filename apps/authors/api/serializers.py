from datetime import date

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.authors.models import Author


class AuthorNameField(serializers.CharField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.trim_whitespace = False
        self.min_length = 1
        self.max_length = 50
    

class AuthorSerializer(serializers.ModelSerializer):
    first_name = AuthorNameField(required=True)
    last_name = AuthorNameField(required=True)

    default_error_messages = {
        "name_already_exists": _("Author with this name already exist"),
        "date_in_future": _("You cannot specify a date in advance"),
        "birth_less_than_death": _("Date of birth must be before date of death")
    }

    class Meta:
        model = Author
        fields = ("id", "first_name", "last_name", "biography", "date_of_birth", "date_of_death")
    
    def _validate_date_in_past(self, _date: date, field: str) -> None:
        if _date >= timezone.now().date():
            raise serializers.ValidationError({
                field: self.default_error_messages["date_in_future"]
            })

    def validate(self, attrs):
        date_of_birth = attrs.get("date_of_birth", self.instance.date_of_birth if self.instance else None)
        date_of_death = attrs.get("date_of_death", self.instance.date_of_death if self.instance else None)
        if date_of_birth:
            self._validate_date_in_past(date_of_birth, "date_of_birth")
        if date_of_death:
            self._validate_date_in_past(date_of_birth, "date_of_death")

        if date_of_birth and date_of_death and date_of_birth >= date_of_death:
            raise serializers.ValidationError({
                "date_of_birth": self.default_error_messages["birth_less_than_death"]
            })

        first_name = attrs.get("first_name", self.instance.first_name if self.instance else None)
        last_name = attrs.get("last_name", self.instance.last_name if self.instance else None)
        if first_name and last_name:
            check_name_q = Author.objects.filter(first_name=first_name, last_name=last_name)
            if self.instance:
                # The same data may be sent during update
                # so we should exclude the current instance from the check
                check_name_q = check_name_q.exclude(id=self.instance.id)

            if check_name_q.exists():
                raise serializers.ValidationError(
                    self.default_error_messages["name_already_exists"],
                    code="name_already_exists"
                )
        return attrs
