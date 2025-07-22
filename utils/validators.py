# utils/validators.py

from django.core.exceptions import ValidationError

def validate_file_size(value):
    max_size_mb = 2  # 2 MB limit
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image file too large (> {max_size_mb}MB).")
