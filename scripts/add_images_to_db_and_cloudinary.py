import os
import load_django
from home.models import Image, Tag
from cloudinary import uploader

ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif')

def upload_local_images_to_db(folder_path, tag_name=None):
    """
    Завантажує фотографії в Cloudinary з оптимізацією (через пресет)
    та створює записи в моделі Image.
    """

    print(f"Починаю сканування папки: {folder_path}")

    successful_uploads = 0

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(ALLOWED_EXTENSIONS):

            file_path = os.path.join(folder_path, filename)
            print(f"Обробка: {filename}")

            try:
                # ЗАВАНТАЖЕННЯ В CLOUDINARY (Cloudinary API)
                result = uploader.upload(
                    file_path,
                    upload_preset='zlaya_zaya_upload_limit_200kb',
                    # Додатково: встановлення папки на Cloudinary
                    folder='zlaya_zaya'
                )

                public_id = result.get('public_id')

                # СТВОРЕННЯ ЗАПИСУ В БАЗІ ДАНИХ (Django ORM)
                Image.objects.create(
                    # Поле CloudinaryField зберігає Public ID
                    image=public_id
                )


                successful_uploads += 1
                print(f"✅ Успіх. Public ID: {public_id}")

            except Exception as e:
                print(f"❌ Помилка завантаження {filename}: {e}")

    print(f"\n--- Завершено. Успішно завантажено {successful_uploads} зображень. ---")


# Запуск функції, якщо це головний скрипт
if __name__ == '__main__':
    # Встановіть тут реальний шлях до папки з фото
    upload_local_images_to_db('../images_to_upload', 'imported')