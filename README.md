# Yatube 

## О проекте

Проект социальной сети Yatube для публиковации собственных 
заметок и возможностью размещаения к ним картинок. Также есть 
возможность смотреть и комментировать заметки других пользователей,
подписываться на понравившихся авторов.

### Используемый стек

Python 3, Django, PostgreSQL, Unittest, Gunicorn, Nginx.

### Как запустить проект

> команды указаны для Windows

Клонировать репозиторий и далее перейти в него.

```sh
git clone git@github.com:AfonyaTriceps/hw05_final.git
```

Cоздать и активировать виртуальное окружение:

```sh
python -m venv venv
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```sh
pip install -r requirements.txt
```

Выполнить миграции:

```sh
python manage.py migrate
```
