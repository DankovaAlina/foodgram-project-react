from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def validate_username_me(value):
    """Проверяет username на использование значения "me"."""
    if value == 'me':
        raise ValidationError(
            'Использовать имя "me" в качестве username запрещено.'
        )
    return value


username_validator = RegexValidator(
    r'^[\w.@+-]+\Z',
    'Поле username не соответствует формату.'
)
