ПРИМИТИВНАЯ СИСТЕМА УПРАВЛЕНИЯ БАЗАМИ ДАННЫХ

Простой модуль для управления структурой базы данных с поддержкой создания и удаления таблиц.

УПРАВЛЕНИЕ ПРОЕКТОМ

Установка зависимостей:
make install
или 
poetry install

Запуск:
make run
или
poetry run database

Сборка пакета:
make build
или
poetry build

Публикация (тестовый режим):
make publish
или
poetry publish --dry-run

Установка пакета локально:
make package-install
или
python3 -m pip install dist/*.whl

Проверка кода:
make lint
или
poetry run ruff check .

УПРАВЛЕНИЕ ТАБЛИЦАМИ

Доступные команды:

● Создание таблицы
  Команда: create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...
  Создает новую таблицу с указанными столбцами. Автоматически добавляет столбец ID:int в качестве первичного ключа.

  Поддерживаемые типы данных:
  • int - целые числа
  • str - строки  
  • bool - логические значения

  Примеры:
  create_table users name:str age:int active:bool
  create_table products title:str price:int

● Удаление таблицы
  Команда: drop_table <имя_таблицы>
  Удаляет таблицу и все связанные с ней метаданные.

  Пример:
  drop_table users
  
  ● Просмотр таблиц
  Команда: list_tables
  Отображает список всех существующих таблиц.

● Справка
  Команда: help
  Показывает список доступных команд и примеры использования.

● Выход
  Команда: exit
  Завершает работу программы.

Пример сессии работы:

Добро пожаловать в модуль 'База данных'!

Введите 'help' для просмотра доступных команд.
Введите 'exit' для выхода из программы.

>>>>Введите команду: create_table users name:str email:str age:int
Таблица 'users' успешно создана

>>>Введите команду: create_table products title:str price:int in_stock:bool  
Таблица 'products' успешно создана

>>>Введите команду: list_tables
Таблицы в базе данных:
1. users
2. products

>>>Введите команду: drop_table products
Таблица 'products' успешно удалена

>>>Введите команду: exit
До свидания!

ДЕМОНСТРАЦИЯ РАБОТЫ
[![asciicast](https://asciinema.org/a/example-id.svg)](https://asciinema.org/a/example-id)
