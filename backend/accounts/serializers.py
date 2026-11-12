from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from progress.models import StudentProgress

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=150, write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)
    email = serializers.EmailField(required=True, max_length=254)
    estado = serializers.ChoiceField(choices=User._meta.get_field('estado').choices, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'full_name', 'rol', 'nivel', 'grado', 'estado']

    def to_internal_value(self, data):
        forbidden = set(data) - set(self.fields)
        if forbidden:
            raise serializers.ValidationError({key: 'Campo no permitido.' for key in forbidden})
        return super().to_internal_value(data)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Este correo ya está registrado. Inicia sesión o solicita la verificación pendiente.')
        return value

    def validate_rol(self, value):
        if value not in [User.Rol.ESTUDIANTE, User.Rol.DOCENTE]:
            raise serializers.ValidationError('No se permite este tipo de cuenta.')
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Las contraseñas no coinciden.'})
        candidate = User(username=data['username'], email=data['email'], first_name=data['full_name'])
        validate_password(data['password'], user=candidate)
        if data.get('rol', User.Rol.ESTUDIANTE) == User.Rol.ESTUDIANTE:
            level, grade = data.get('nivel'), data.get('grado')
            if level not in User.Nivel.values or grade is None or not 1 <= grade <= (3 if level == User.Nivel.SECUNDARIA else 6):
                raise serializers.ValidationError({'grado': 'Selecciona un año (1–3) o semestre (1–6) válido.'})
        else:
            data['nivel'], data['grado'] = '', None
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        full_name = validated_data.pop('full_name')
        user = User.objects.create_user(**validated_data, first_name=full_name,
            alias=full_name[:50], email_status=User.EmailStatus.PENDING)
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
            "first_name",
            "last_name",
            "email",
            "estado",
            "email_status",
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


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Only self-service fields; identity, roles and permissions are not editable."""
    class Meta:
        model = User
        fields = ["first_name", "last_name", "alias", "nivel", "grado", "estado"]

    def to_internal_value(self, data):
        forbidden = set(data) - set(self.fields)
        if forbidden:
            raise serializers.ValidationError({key: "Este campo no se puede editar." for key in forbidden})
        return super().to_internal_value(data)

    def validate(self, data):
        level = data.get("nivel", self.instance.nivel)
        grade = data.get("grado", self.instance.grado)
        if self.instance.rol == User.Rol.ESTUDIANTE:
            maximum = 3 if level == User.Nivel.SECUNDARIA else 6
            if not level or grade is None or not 1 <= grade <= maximum:
                raise serializers.ValidationError({"grado": "Indica un grado válido: secundaria 1–3 o bachillerato 1–6."})
        elif "nivel" in data or "grado" in data:
            raise serializers.ValidationError("Los datos académicos de esta cuenta no son editables desde el perfil.")
        return data
