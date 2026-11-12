from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from progress.models import StudentProgress

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "rol", "nivel", "grado", "alias"]

    def validate_password(self, value):
        validate_password(value)  # aplica las reglas de settings.py
        return value

    def validate_rol(self, value):
        if value == User.Rol.ADMIN:
            raise serializers.ValidationError("No se puede registrar como administrador.")
        return value

    def validate(self, data):
        if data.get("rol", User.Rol.ESTUDIANTE) == User.Rol.ESTUDIANTE:
            if not data.get("nivel") or not data.get("grado"):
                raise serializers.ValidationError("Un estudiante debe indicar nivel y grado.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        StudentProgress.objects.get_or_create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    xp = serializers.SerializerMethodField()
    streak_days = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "rol",
            "nivel",
            "grado",
            "alias",
            "ranking_publico",
            "xp",
            "streak_days",
        ]

    def get_xp(self, obj):
        progress, _ = StudentProgress.objects.get_or_create(user=obj)
        return progress.xp

    def get_streak_days(self, obj):
        progress, _ = StudentProgress.objects.get_or_create(user=obj)
        return progress.streak_days
