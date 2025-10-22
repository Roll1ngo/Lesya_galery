import cloudinary
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .models import Image
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    images = Image.objects.all().order_by("-id")
    context = {"images": images}
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
        image_title = request.POST.get("title")
        image_file = request.FILES.get("image")  # Змінено ім'я змінної, щоб не конфліктувало з моделлю

        # CloudinaryField АВТОМАТИЧНО обробляє завантаження,
        # коли об'єкт моделі зберігається в базі даних.
        if image_file:
            Image.objects.create(title=image_title, image=image_file)
            messages.success(request, "Uploaded Successfully to Cloudinary!")
            return redirect("index")
        else:
            messages.error(request, "No image file provided.")
            # Використовуйте render замість redirect, щоб не втрачати контекст
            return render(request, "upload.html")

    return render(request, "upload.html")


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
