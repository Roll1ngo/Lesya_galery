import subprocess
import sys
import os

def run_gunicorn():
    """
    Запускає Gunicorn із визначеними аргументами.
    Використовує gevent як клас воркера для кращої асинхронної обробки.
    """
    # Перевіряємо, чи встановлений gevent, оскільки він зазначений у параметрі --worker-class
    try:
        import gevent
    except ImportError:
        print("Помилка: Необхідна бібліотека 'gevent' не встановлена.", file=sys.stderr)
        print("Будь ласка, виконайте: pip install gevent", file=sys.stderr)
        sys.exit(1)

    # Команда Gunicorn, розбита на список аргументів
    command = [
        'gunicorn',
        'django_images.wsgi:application',
        '--bind', '0.0.0.0:8000',
        '--workers', '4',
        '--timeout', '60',
        '--worker-class', 'gevent'
    ]

    print(f"Запуск Gunicorn з командою: {' '.join(command)}")
    print("Натисніть Ctrl+C для зупинки.")

    try:
        # Запускаємо команду. check=True змусить Python згенерувати виняток,
        # якщо Gunicorn завершиться з помилкою.
        subprocess.run(command, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Помилка: Gunicorn завершився з кодом помилки {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        # Обробка Ctrl+C для коректного виходу
        print("\nСервер зупинено...")
        sys.exit(0)
    except FileNotFoundError:
        print("Помилка: Команда 'gunicorn' не знайдена. Переконайтеся, що ви активували ваше віртуальне середовище (.venv) і Gunicorn встановлений.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_gunicorn()
