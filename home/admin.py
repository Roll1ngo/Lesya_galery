from django.contrib import admin
from .models import *


# Register your models here.
class ImageAdmin(admin.ModelAdmin):
    list_display = ["image", "uploaded_at"]


admin.site.register(Image, ImageAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "material_icon"]

admin.site.register(Tag, TagAdmin)
