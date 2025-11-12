from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path('delete/<int:image_id>/<str:backref>/', views.delete_image, name='delete_image'),
    path('download/<int:image_id>/', views.download_image, name='download_image'),
    path('next_todo/', views.next_todo, name='next_todo'),
    path('api/toggle-tag/', views.toggle_tag_view, name='toggle_tag'),
    path("upload/", views.upload, name="upload"),
    path("signup/", views.signup, name="signup"),
    path("logout_page/", views.logout_page, name="logout_page"),
    path("login/", views.login_page, name="login_page"),
    path("help_page/", views.help_page, name="help_page"),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
