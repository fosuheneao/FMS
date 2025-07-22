# utils/image_processing.py

from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def resize_image(image_field, max_width=1024):
    image = Image.open(image_field)
    if image.width > max_width:
        ratio = max_width / float(image.width)
        height = int(float(image.height) * float(ratio))
        image = image.resize((max_width, height), Image.ANTIALIAS)

        image_io = BytesIO()
        image.save(image_io, format='JPEG', quality=85)
        return ContentFile(image_io.getvalue(), name=image_field.name)
    return image_field
