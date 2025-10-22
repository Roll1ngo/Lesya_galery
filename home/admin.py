from django.contrib import admin
from .models import *


# Register your models here.
class ImageAdmin(admin.ModelAdmin):
    list_display = ["title", "image", "uploaded_at"]


admin.site.register(Image, ImageAdmin)
