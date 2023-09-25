
from django.forms import ValidationError


def validate_file_size(file):
    max_size_kb = 50
    if file.size > max_size_kb * 1024:
        raise ValidationError(f'File must be less than or equal {max_size_kb}')
