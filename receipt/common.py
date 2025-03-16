import os
from datetime import datetime
from django.db import models


class DatedModel(models.Model):
    date: models.DateField  # type: ignore

    class Meta:
        abstract = True

def get_photo_upload_path(instance: DatedModel, filename: str) -> str:
    """
    Generates a path to save the photo in the format:
    model_name/YYYY/MM/DD/filename
    """

    date_str = instance.date.strftime('%Y/%m/%d') if instance.date else datetime.now().strftime('%Y/%m/%d')
    model_name = instance.__class__.__name__.lower()
    return os.path.join(model_name, date_str, filename)
