# Используем официальный образ Python в качестве базового образа
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /usr/src/app

# Копируем файл requirements.txt и устанавливаем зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . .

# Указываем команду по умолчанию
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]