from django.db import models
from cloudinary.models import CloudinaryField
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Назва тегу")
    slug = models.SlugField(unique=True, blank=True)
    material_icon = models.CharField(
        max_length=50,
        default='tag',
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Image(models.Model):
    image = CloudinaryField('image')
    tags = models.ManyToManyField(Tag, related_name='images', blank=True, verbose_name="Теги")
    uploaded_at = models.DateTimeField(auto_now=True)
