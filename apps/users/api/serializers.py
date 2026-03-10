from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import PasswordField

from apps.users.verify import EmailVerificationCode
from apps.users.tasks import send_verification_code

UserModel = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    username_field = UserModel.USERNAME_FIELD
    password = PasswordField(write_only=True, validators=[validate_password])
    success_message = _("Successfully registered, please log in.")

    default_error_messages = {
        "already_exists": _("Already exists")
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        match self.username_field:
            case "email":
                self.fields[self.username_field] = serializers.EmailField(write_only=True)
            case "username":
                self.fields[self.username_field] = serializers.CharField(
                    write_only=True,
                    validators=[UnicodeUsernameValidator()],
                )
            case _:
                self.fields[self.username_field] = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_value = attrs[self.username_field]
        if UserModel.objects.filter(**{self.username_field: username_value}).exists():
            raise serializers.ValidationError(
                {self.username_field: self.default_error_messages["already_exists"]}
            )
        return attrs

    def create(self, validated_data):
        username_value = validated_data[self.username_field]
        password = validated_data["password"]

        kwargs = {self.username_field: username_value, "password": password, "email_verified": False}

        if self.username_field != "username":
            kwargs["username"] = username_value.split("@")[0]

        user = UserModel.objects.create_user(**kwargs)
        if user.email and user.email_verified is False:
            try:
                send_verification_code.delay(user.email)
            except:
                # fail silently
                pass
        return user


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    code = serializers.CharField(write_only=True, max_length=6)
    default_error_messages = {
        "invalid_code": _("Invalid code"),
        "not_exist": _("No active account with this email"),
    }

    def validate(self, attrs):
        email, code = attrs["email"], attrs["code"]
        if not UserModel.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": self.default_error_messages["not_exist"]})
            
        if not EmailVerificationCode.verify(email, code):
            raise serializers.ValidationError({"code": self.default_error_messages["invalid_code"]})
        
        UserModel.objects.filter(email=email).update(email_verified=True)
        return attrs
