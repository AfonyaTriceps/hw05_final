from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def image(name: str = 'giffy.gif') -> SimpleUploadedFile:
    small_gif = Image.new('RGBA', (200, 200), 'white')
    file = BytesIO()
    small_gif.save(file, format='PNG')
    return SimpleUploadedFile(
        name=name,
        content=file.getvalue(),
        content_type='image/gif',
    )
