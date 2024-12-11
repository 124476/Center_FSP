# Center FSP
## Платформа, которая улучшит координацию между ФСП и регионами, упростит процессы подачи и обработки заявок, а также повысит качество общения и управления данными.
***

### Инструкция по запуску проекта
Все команды вводятся в терминале.  
**Необходимо иметь установленные pip и python для терминала.**

#### Клонируем проект

```commandline
git clone https://github.com/hackathonsrus/pp_final_20299_pfo_ta_litseisti_kfu_102
```

#### Переходим в папку pp_final_20299_pfo_ta_litseisti_kfu_102

```commandline
cd pp_final_20299_pfo_ta_litseisti_kfu_102
```

#### Создайте в коренной папке проекта файл `.env` рядом с `center_fsp`

***Для Linux системы используйте следующую команду***
```commandline
touch .env
```

#### Скопируйте содержимое `.env.example` в `.env`
#### Windows
Если вы используете командную строку (cmd):
```commandline
copy .env.example .env
```
Если вы используете PowerShell:
```commandline
Copy-Item .env.example .env
```
***

#### Linux / macOS
В терминале используйте команду:
```commandline
cp .env.example .env
```

### Команды для запуска проекта с Docker - PostgreSQL

***Для этого варианта требуется установленный Docker, а также в `.env` нужно 
прописать значение `USE_DOCKER=True`***
***

#### 1. Для билда Docker-образа используйте команду:
```commandline
docker build . -t=py-server:local
```

#### 2. Пропишите миграцию базы данных и создайте супер юзера:
```commandline
docker exec -it django bash
python manage.py migrate
python manage.py createsuperuser
exit
```

#### 3. Запустите контейнер при помощи Docker Compose:
```commandline
docker compose up
```

### Команды для запуска проекта без Docker - SQLite
***Для этого варианта требуется прописать значение в `.env` `USE_DOCKER=False`***
***

#### 1. Создаём и активируем виртуальное окружение
Рекомендуется использовать виртуальное окружение для изоляции зависимостей:<br>
Для Windows:
```commandline
python -m venv venv
venv\Scripts\activate
```

Для MacOS/Linux:
```commandline
python3 -m venv venv
source venv/bin/activate
```

#### 2. Устанавливаем зависимости

```commandline
pip install -r requirements.txt
```

#### 3. Переходим в папку с manage.py

```commandline
cd center_fsp
```

#### 4. Настраиваем миграции

```commandline
python manage.py migrate
```

#### 5. Запускаем сервер 

```commandline
python manage.py runserver
```

#### 6. Переходим на сайт

<a href="http://127.0.0.1:8000/">http://127.0.0.1:8000/</a>

***Терминал не закрываем!***

### Возможные ошибки запуска
#### В случае возникновения ошибки с venv\Scripts\activate 

Решение проблемы:
- Открываем терминал PowerShell от админа.
- Вставляем и запускаем `Set-ExecutionPolicy RemoteSigned`
- На вопрос отвечаем `A`
- Продолжаем запускать проект по инструкции README.md с `Создаём и активируем виртуальное окружение`

#### Ошибка при загрузке requirements

Если у вас установлены несколько версий Python, используйте путь к нужной версии. Например, чтобы использовать Python 3.8, выполните команду:

**На Windows:**
```commandline
C:\path\to\python3.8\python.exe -m venv venv
```

Замените `C:\path\to\python3.8\python.exe` на путь к нужной версии Python, которую вы хотите использовать.

**На macOS/Linux:** <br>
Если у вас установлена нужная версия Python, вы можете использовать команду: <br>
```commandline
python3.8 -m venv venv
```

### Хостинг

<a href="https://mario12508.pythonanywhere.com/">https://mario12508.pythonanywhere.com/</a>

Представитель ФСП (суперюзер)
```
Логин: admin_fsp
Пароль: admin123
```

Представители регионов

| Регион  | Логин | Пароль |
|---------|-------|--------|
| донецкая народная республика | IGOR | донецкаянароднаяреспублика |
| алтайский край | Svetlana | алтайская |
| республика Адыгея | Marat | адыгеямарат |
| курганская область | Michail | курганская |
| камчатский край | Vladimir | камчатка |

### Видеодемонстрация

<a href="https://disk.yandex.ru/i/QcpC5Ad38EOOsw">https://disk.yandex.ru/i/QcpC5Ad38EOOsw</a>

[Скачать видеодемонстрацию проекта](https://github.com/hackathonsrus/pp_final_20299_pfo_ta_litseisti_kfu_102/raw/main/Видеодемонстрация.mp4)
