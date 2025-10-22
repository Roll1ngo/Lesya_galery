from django.db import models
from cloudinary.models import CloudinaryField


# Create your models here.


class Image(models.Model):
    title = models.CharField(max_length=100)
    image = CloudinaryField('image')
    uploaded_at = models.DateTimeField(auto_now=True)
