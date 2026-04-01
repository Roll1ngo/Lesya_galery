import json
from datetime import timedelta
from io import BytesIO

import cloudinary
import requests
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone

from .models import Image, Tag

HELP_VIEWED_MARKER_COOKIE = 'first_visit_done'

def index(request):
    # Отримуємо параметри сортування з GET-запиту
    sort_by = request.GET.get('sort', 'newest')
    category_id = request.GET.get('category', 'all')
    if request.COOKIES.get(HELP_VIEWED_MARKER_COOKIE) is None:
        print("Redirecting to help page for first visit.")
        # Додаємо параметр 'from_first_visit' для ідентифікації
        # Цей параметр потрібен, якщо ми хочемо обробляти кешування лише при першому візиті.
        return redirect(reverse('help_page') + '?first=true')
    print("Not the first visit or help already viewed.")
    # Базовий queryset
    images = Image.objects.all()

    # СОРТУВАННЯ
    if sort_by == 'newest':
        images = images.order_by('-uploaded_at')
    elif sort_by == 'oldest':
        images = images.order_by('uploaded_at')

    elif sort_by == 'trending':
        # Трендові (за останній тиждень)
        week_ago = timezone.now() - timedelta(days=7)
        images = images.filter(uploaded_at__gte=week_ago).order_by('-id')

    # ФІЛЬТРАЦІЯ ПО КАТЕГОРІЯХ (ТЕГАХ)
    if category_id != 'all':
        try:
            images = images.filter(tags__id=category_id).distinct()
        except ValueError:
            # Якщо category_id не число (наприклад, 'all')
            pass

    tags = Tag.objects.all()

    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(
        keyword in user_agent for keyword in ['android', 'iphone', 'ipad', 'ipod', 'mobile', 'windows phone'])
    is_desktop = not is_mobile

    context = {
        "images": images,
        'is_desktop': is_desktop,
        'all_tags': tags,
        'current_sort': sort_by,
        'current_category': category_id,
    }
    return render(request, "index.html", context)


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Password doesn't match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            User.objects.create_user(username=username, email=email, password=password2)
            messages.success(request, "Account Created Successfully!")
            return redirect("login_page")
    return render(request, "signup.html")


def login_page(request):
    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        messages.success(request, "Logged In Successfully!")
        return redirect("index")
    else:
        # messages.error(request, "Invalid username or password")
        return redirect("login_page")
    return render(request, "login.html")


def upload(request):
    if request.method == "POST":
        print("uploading...")
        image_file = request.FILES.get("image")
        checked_image_file = resmush_service_quality_reduction(image_file) if image_file.size > 1 * 1024 * 1024 else image_file
        checked_image_file = image_file if checked_image_file is None else checked_image_file
        if checked_image_file is image_file:
            image_file.seek(0)
        selected_tags = request.POST.getlist("tags")  # Отримуємо список вибраних тегів

        if image_file:
            # Створюємо зображення без назви
            image = Image.objects.create(image=checked_image_file)

            # Додаємо вибрані теги
            if selected_tags:
                tags = Tag.objects.filter(id__in=selected_tags)
                image.tags.set(tags)

            messages.success(request, "Зображення успішно завантажено!")
            return redirect("index")
        else:
            messages.error(request, "Будь ласка, виберіть файл зображення.")
            return render(request, "upload.html", {'all_tags': Tag.objects.all()})

    # GET запит - показуємо форму з усіма тегами
    return render(request, "upload.html", {'all_tags': Tag.objects.all()})


def logout_page(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return redirect("index")

@login_required
def delete_image(request, image_id):
    # Отримуємо об'єкт, або повертаємо 404
    image_instance = get_object_or_404(Image, id=image_id)

    # Перевірка прав доступу (тільки для суперкористувачів, як у вашій навігації)
    if not request.user.is_superuser:
        messages.error(request, "У вас немає дозволу на видалення цього зображення.")
        return redirect('index')

    try:
        # 1. ОТРИМАННЯ PUBLIC ID З CLOUDINARY FIELD
        # CloudinaryField зберігає Public ID у властивості field.public_id
        public_id = image_instance.image.public_id

        # 2. ВИДАЛЕННЯ З CLOUDINARY
        # Викликаємо функцію destroy() Cloudinary
        response = cloudinary.uploader.destroy(public_id)

        # Перевірка, чи Cloudinary успішно видалив файл
        if response.get('result') == 'ok' or response.get('result') == 'not found':

            # 3. ВИДАЛЕННЯ З БАЗИ ДАНИХ DJANGO
            image_instance.delete()
            messages.success(request, "Зображення та відповідний файл у Cloudinary успішно видалено!")
        else:
            # Обробка помилки Cloudinary (наприклад, якщо Public ID не знайдено)
            messages.warning(request, f"Зображення видалено з бази даних, але виникла помилка при видаленні з Cloudinary: {response.get('result')}")
            image_instance.delete() # Якщо Cloudinary видалив, але результат не 'ok', краще видалити і з бази

    except Exception as e:
        messages.error(request, f"Виникла непередбачена помилка: {e}")

    return redirect('index')


def download_image(request, image_id):
    # 1. Отримуємо об'єкт зображення
    image_obj = get_object_or_404(Image, id=image_id)

    # 2. Отримуємо шлях до файлу
    file_path = image_obj.image.path

    # 3. Визначаємо ім'я файлу, яке має бути на клієнті
    # Використовуємо ім'я з параметрів, якщо воно є (для зручності)
    client_filename = request.GET.get('filename')
    if not client_filename:
        # Якщо ім'я не передано, використовуємо назву зображення
        client_filename = f"{image_obj.title}.jpg"

    # 4. Створюємо відповідь FileResponse
    try:
        response = FileResponse(open(file_path, 'rb'))
    except FileNotFoundError:
        raise Http404("Файл не знайдено.")

    # 5. ВСТАНОВЛЕННЯ ЗАГОЛОВКА, ЩО ПРИМУСОВО ВИКЛИКАЄ ВІКНО ЗБЕРЕЖЕННЯ
    # Це КЛЮЧОВИЙ момент для коректної роботи на ПК та Android
    response['Content-Type'] = 'application/octet-stream'  # Загальний тип для завантаження
    response['Content-Disposition'] = f'attachment; filename="{client_filename}"'

    return response


# Helper-функція для перевірки, чи є користувач суперкористувачем
def is_superuser(user):
    """Перевіряє, чи є користувач автентифікованим і суперкористувачем."""
    return user.is_authenticated and user.is_superuser



@require_http_methods(["POST"])
@user_passes_test(is_superuser, login_url='/admin/login/')
def toggle_tag_view(request):
    """
    Обробляє AJAX-запити на додавання або видалення тегів до/з зображення.
    Очікує JSON-дані: {'image_id': int, 'tag_id': int, 'action': 'add'/'remove'}
    """
    if not request.body:
        return JsonResponse({'status': 'error', 'message': 'Відсутнє тіло запиту.'}, status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
        image_id = data.get('image_id')
        tag_id = data.get('tag_id')
        action = data.get('action')  # 'add' або 'remove'

        # Отримуємо об'єкти або викликаємо 404
        image = get_object_or_404(Image, id=image_id)
        tag = get_object_or_404(Tag, id=tag_id)

        if action == 'add':
            image.tags.add(tag)
            message = f"Тег '{tag.name}' додано до зображення."
        elif action == 'remove':
            image.tags.remove(tag)
            message = f"Тег '{tag.name}' видалено із зображення."
        else:
            return JsonResponse({'status': 'error', 'message': 'Невідома дія (action).'}, status=400)

        return JsonResponse({'status': 'success', 'message': message})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Неправильний формат JSON.'}, status=400)
    except Exception as e:
        # Обробка інших можливих помилок, наприклад, помилок бази даних
        return JsonResponse({'status': 'error', 'message': f'Внутрішня помилка сервера: {str(e)}'}, status=500)


def help_page(request):
    """Виводить сторінку довідки."""

    # Перевіряємо, чи це перехід з першого візиту
    is_first_visit_redirect = request.GET.get('first') == 'true'

    context = {
        'is_first_visit_redirect': is_first_visit_redirect
    }

    # render(request, "help.html", context)
    return render(request, "help.html", context)  # Припустімо, що ваш шаблон називається help.html


def resmush_service_quality_reduction(image):
    api_url= "http://api.resmush.it/?qlty=20"
    try:
        response = requests.post(api_url, files={"files": image})
        if response.status_code == 200:
            response_data = response.json()
            reduced_image_url = response_data.get("dest")
            reduced_image_bytes = requests.get(reduced_image_url).content
            print(f"✅ Зображення успішно зменшено через Resmush.it")
            print(f"Original size: {image.size} bytes, Reduced size: {len(reduced_image_bytes)} bytes")
            return InMemoryUploadedFile(
                        file=BytesIO(reduced_image_bytes),
                        field_name='image',
                        name=f"reduced_{image.name}",
                        content_type=image.content_type,
                        size=len(reduced_image_bytes),
                        charset=None
                    )
    except requests.exceptions.RequestException as e:
        print(f"❌ Помилка при зверненні до API: {e}")
    except json.JSONDecodeError:
        print(f"❌ Помилка: Не вдалося розібрати JSON-відповідь. Відповідь: {response.text[:100]}...")

