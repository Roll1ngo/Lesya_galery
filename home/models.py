from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Image(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="user_images")
    date = models.DateTimeField(auto_now=True)
