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
  create_table users name:str age:int active:bool email:str
  create_table products name:str price:int category:str in_stock:bool

● Удаление таблицы
  
  Команда: drop_table <имя_таблицы>
  Удаляет таблицу и все связанные с ней метаданные.

  Пример:
  drop_table users
  
● Просмотр таблиц
  Команда: list_tables
  Отображает список всех существующих таблиц.
  
● Просмотр информации о таблице
  info <имя_таблицы>
  Выводит информацию о названии таблицы, столбцах и количестве записей

ОПЕРАЦИИ С ДАННЫМИ (CRUD)

● CREATE - Добавление записей
  
  Команда: insert into <имя_таблицы> values (<значение1>, <значение2>, ...)

  Примеры:
  insert into users values ("Alice", 25, true, "alice@mail.com")
  insert into products values ("Laptop", 1000, "Electronics", true)

● READ - Чтение записей

  Чтение всех записей:
  Команда: select from <имя_таблицы>

  Чтение с фильтрацией:
  Команда: select from <имя_таблицы> where <столбец> = <значение>

  Примеры:
  select from users where age = 25
  select from users where name = "Alice"
  select from users where active = true

● UPDATE - Обновление записей

  Команда: update <имя_таблицы> set <столбец1> = <новое_значение> where <условие>
  
  Примеры:
  update users set age = 26 where name = "Alice"
  update users set active = false where age > 30
  update users set email = "new@mail.com", age = 27 where name = "Bob"

● DELETE - Удаление записей

  Команда: delete from <имя_таблицы> where <условие>

  Примеры:
  delete from users where name = "Alice"
  delete from users where active = false

ОБЩИЕ КОМАНДЫ

● Справка
  Команда: help
  Показывает список доступных команд и примеры использования.

● Выход
  Команда: exit
  Завершает работу программы.

ОСОБЕННОСТИ СИСТЕМЫ

Автоинкремент ID
- Каждая таблица автоматически получает столбец ID
- ID генерируются автоматически и гарантируют уникальность
- При удалении записей освободившиеся ID могут переиспользоваться

Регистронезависимость
- Имена таблиц и столбцов не чувствительны к регистру
- Работают команды в любом регистре: SELECT, select, Select

Поддержка пробелов в значениях
Значения с пробелами должны заключаться в кавычки:
insert into users values ("John Doe", 30, true, "john.doe@mail.com")
select from users where name = "John Doe"

Форматы булевых значений
Поддерживаются различные форматы:
- true, false
- 1, 0
- yes, no
- on, off

ДЕКОРАТОРЫ ДЛЯ ОБРАБОТКИ ОШИБОК И ЛОГИРОВАНИЯ

Система использует декораторы для централизованной обработки различных аспектов работы:

- @handle_db_errors - перехватывает и обрабатывает все ошибки базы данных:
  • FileNotFoundError - файлы данных не найдены
  • PermissionError - недостаточно прав для доступа к файлам  
  • KeyError - обращение к несуществующим таблицам/столбцам
  • ValueError - ошибки валидации типов данных
  • JSONDecodeError - ошибки парсинга JSON
  • Exception - все остальные непредвиденные ошибки

- @confirm_action - запрашивает подтверждение для опасных операций:
  • Удаление таблиц (drop_table)
  • Удаление записей (delete)
  • Поддерживает ответы y/n с возможностью отмены операции

- @log_time - замеряет время выполнения функций:
  • Выводит время выполнения в секундах
  • Помогает в профилировании и оптимизации запросов

СИСТЕМА КЭШИРОВАНИЯ ЗАПРОСОВ

Реализовано интеллектуальное кэширование результатов SELECT-запросов:

- Автоматическое кэширование результатов запросов
- Ключи кэша формируются на основе таблицы и условий WHERE
- При изменении данных (INSERT, UPDATE, DELETE) кэш автоматически инвалидируется
- Повторные одинаковые запросы выполняются мгновенно из кэша

Пример работы кэширования:
>>> select from users where age = 25  # Выполняется и кэшируется
>>> select from users where age = 25  # Возвращается из кэша
>>> insert into users values ("New User", 30, true, new@email.com)  # Кэш инвалидируется
>>> select from users where age = 25  # Выполняется заново и кэшируется

ПРИМЕР СЕССИИ РАБОТЫ

Добро пожаловать в модуль 'База данных'!

Введите 'help' для просмотра доступных команд.
Введите 'exit' для выхода из программы.

>>>>Введите команду: create_table users name:str email:str age:int
Таблица 'users' успешно создана

>>>Введите команду: create_table products title:str price:int category:str in_stock:bool  
Таблица 'products' успешно создана

>>>Введите команду: list_tables
Таблицы в базе данных:
1. users
2. products

>>>Введите команду: insert into products values ("Laptop", 1000, "Electronics", true)
Файл метаданных 'data/products.json' создан
Функция insert выполнилась за 0.001 секунд
Запись успешно добавлена с ID: 1

>>>Введите команду: insert into products values ("Mouse", 25, "Electronics", 0)
Функция insert выполнилась за 0.001 секунд
Запись успешно добавлена с ID: 2


>>>Введите команду: select from products
Функция select выполнилась за 0.000 секунд
+----+--------+-------+-------------+----------+
| ID | title  | price |   category  | in_stock |
+----+--------+-------+-------------+----------+
| 1  | Laptop |  1000 | Electronics |   True   |
| 2  | Mouse  |   25  | Electronics |  False   |
+----+--------+-------+-------------+----------+

>>>Введите команду: select from products where title = "Mouse"
Функция select выполнилась за 0.000 секунд
+----+-------+-------+-------------+----------+
| ID | title | price |   category  | in_stock |
+----+-------+-------+-------------+----------+
| 2  | Mouse |   25  | Electronics |  False   |
+----+-------+-------+-------------+----------+

>>>Введите команду: update products set price = 30 where title = "Mouse"
Обновлено записей: 1

>>>Введите команду: select from products
Функция select выполнилась за 0.000 секунд
+----+--------+-------+-------------+----------+
| ID | title  | price |   category  | in_stock |
+----+--------+-------+-------------+----------+
| 1  | Laptop |  1000 | Electronics |   True   |
| 2  | Mouse  |   30  | Electronics |  False   |
+----+--------+-------+-------------+----------+


>>>Введите команду: delete from products where in_stock = false
Вы уверены, что хотите выполнить "удаление записей"? [y/n]: y
Удалено записей: 1

>>>Введите команду: Функция select выполнилась за 0.000 секунд
+----+--------+-------+-------------+----------+
| ID | title  | price |   category  | in_stock |
+----+--------+-------+-------------+----------+
| 1  | Laptop |  1000 | Electronics |   True   |
+----+--------+-------+-------------+----------+

>>>Введите команду: drop_table products
Вы уверены, что хотите выполнить "удаление таблицы"? [y/n]: y
Таблица 'products' успешно удалена
Файл данных 'products.json' удален


>>>Введите команду: exit
До свидания!

ДЕМОНСТРАЦИЯ РАБОТЫ

Установка, запуск базы данных, создание, удаление и просмотр таблиц:
https://asciinema.org/a/W4U5wi4eB3eefAindn7JuGhqK

Работа команд CRUD:
https://asciinema.org/a/FXFfnZ9P5uTGQ1en1RDeMIpzu

Работа декораторов и кэша:
https://asciinema.org/a/VOsY2hJ5WzVG25p8B9JOZafeu

Работа всех функций программы:
https://asciinema.org/a/gKZk23Jmwycpda48FMtAIDxDP

