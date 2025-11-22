import shlex

import prompt

import os

from .core import (
    create_table,
    drop_table,
    list_tables,
    create_insert_function,
    select,
    update,
    delete,
    display_table,
)
from .utils import (
    load_metadata,
    save_metadata,
    METADATA_FILE,
    DATA_DIR,
    load_table_data,
    save_table_data,
    get_next_id,
    normalize_table_schema
)
from .parser import (
    parse_conditions,
    convert_where_clause,
    split_by_commas,
    validate_where_conditions,
    validate_set_conditions
)

def run():
    """
    Главная функция с основным циклом программы.
    """

    print("Добро пожаловать в модуль 'База данных'!\n")
    print("Введите 'help' для просмотра доступных команд.")
    print("Введите 'exit' для выхода из программы.")

    while True:

        try:
            metadata = load_metadata(METADATA_FILE)

            user_input = prompt.string("\n>>>Введите команду: ").strip()

            if user_input.lower() in ["exit", "quit", "выход"]:
                print("До свидания!")
                break

            if not user_input:
                continue

            args = shlex.split(user_input)
            command = args[0].lower()

            match command:

                case "help":
                    print_help()

                case "create_table":
                    if len(args) < 3:
                        print("Ошибка: Недостаточно аргументов для create_table")
                        print(
                            "Использование: create_table <имя_таблицы> "
                            "<столбец1:тип> <столбец2:тип> ..."
                        )
                        continue

                    table_name = args[1]
                    columns_list = args[2:]
                    columns_dict = {}

                    for item in columns_list:

                        if ":" not in item:
                            print(f"Ошибка: Неверный формат '{item}'.")
                            print("Используйте 'столбец:тип'")
                            break
                        col_name, col_type = item.split(":", 1)
                        col_type = col_type.lower().strip()

                        columns_dict[col_name] = col_type

                    new_metadata = create_table(metadata, table_name, columns_dict)

                    if new_metadata != metadata:
                        save_metadata(METADATA_FILE, new_metadata)

                case "drop_table":
                    if len(args) < 2:
                        print("Ошибка: Недостаточно аргументов для drop_table")
                        print("Использование: drop_table <имя_таблицы>")
                        continue

                    table_name = args[1]
                    new_metadata = handle_drop_table(metadata, table_name)
                    save_metadata(METADATA_FILE, new_metadata)

                case "list_tables":
                    list_tables(metadata)

                case "insert":
                    handle_insert(metadata, args)

                case "select":
                    handle_select(metadata, args)

                case "update":
                    handle_update(metadata, args)

                case "delete":
                    handle_delete(metadata, args)

                case "info":
                    handle_info(metadata, args)

                case _:
                    print(f"Функции '{command}' нет. Попробуйте снова.")
                    print("Введите 'help' для просмотра доступных команд.")

        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем. До свидания!")
            break
        except EOFError:
            print("\nДо свидания!")
            break
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    run()


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись"
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию"
    )
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись"
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def handle_insert(metadata, args):
    """
    Обрабатывает команду insert в формате: insert into <table> values (val1, val2, ...)
    """

    if len(args) < 5:
        print("Ошибка: Недостаточно аргументов для insert")
        print(
            "Использование: insert into <имя_таблицы> values (<значение1>, <значение2>, ...)"
        )
        return

    if args[1].lower() != "into":
        print("Ошибка: Ожидается ключевое слово 'into'")
        print(
            "Использование: insert into <имя_таблицы> values (<значение1>, <значение2>, ...)"
        )
        return
    
    table_name = args[2].lower()
    if table_name not in metadata:
        print(f"Ошибка: Таблица '{table_name}' не существует")
        return

    if args[3].lower() != "values":
        print("Ошибка: Ожидается ключевое слово 'values'")
        return

    table_schema = metadata[table_name]
    expected_columns = [col for col in table_schema.keys() if col != "ID"]

    values_str = " ".join(args[4:])

    has_opening_bracket = values_str.startswith('(')
    has_closing_bracket = values_str.endswith(')')
    
    if not has_opening_bracket and not has_closing_bracket:
        print("Ошибка: Отсутствуют скобки вокруг значений")
        print("Использование: values (<значение1>, <значение2>, ...)")
        return
    elif not has_opening_bracket:
        print("Ошибка: Отсутствует открывающая скобка '('")
        print("Использование: values (<значение1>, <значение2>, ...)")
        return
    elif not has_closing_bracket:
        print("Ошибка: Отсутствует закрывающая скобка ')'")
        print("Использование: values (<значение1>, <значение2>, ...)")
        return

    # Убираем внешние скобки
    values_str = values_str[1:-1]

    try:
        values = split_by_commas(values_str)
        values = [v.strip() for v in values]

    except Exception as e:
        print(f"Ошибка при разборе значений: {e}")
        return

    if len(values) != len(expected_columns):
        print(f"Ошибка: Неверное количество значений")
        print(
            f"Ожидается: {len(expected_columns)} (столбцы: {', '.join(expected_columns)})"
        )
        print(f"Получено: {len(values)}")
        return

    insert = create_insert_function(get_next_id)
    new_record = insert(metadata, table_name, values)

    
    table_schema = metadata[table_name]
    expected_columns = [col for col in table_schema.keys() if col != "ID"]

    if len(values) != len(expected_columns):
        print(f"Ошибка: Неверное количество значений")
        print(
            f"Ожидается: {len(expected_columns)} (столбцы: {', '.join(expected_columns)})"
        )
        print(f"Получено: {len(values)}")
        return

    if new_record:
        table_data = load_table_data(table_name)

        table_data.append(new_record)

        if save_table_data(table_name, table_data):
            print(f"Запись успешно добавлена с ID: {new_record['ID']}")
        else:
            print("Ошибка при сохранении данных")


def handle_select(metadata, args):
    """
    Обрабатывает команду select в формате: select from <table> where <столбец> = <значение>
    """
    
    if len(args) < 3:
        print("Ошибка: Недостаточно аргументов для select")
        print("Использование: select from <имя_таблицы> where <столбец> = <значение>")
        return

    if args[1].lower() != "from":
        print("Ошибка: Ожидается ключевое слово 'from'")
        return

    if not validate_where_conditions(args, 4):  # начинаем с индекса 4 (после 'where')
            return
    
    table_name = args[2].lower()
    
    if table_name not in metadata:
        print(f"Ошибка: Таблица '{table_name}' не существует")
        return

    table_schema = metadata[table_name]
    table_schema_norm = normalize_table_schema(table_schema)

    if len(args) == 3:
        table_data = load_table_data(table_name)
        if not table_data:
            print(f"Таблица '{table_name}' пуста")
            return
        
        result_data = select(table_data, None)  # None означает "все записи"
        columns = list(table_schema)
        display_table(result_data, columns)
        return

    
    if args[3].lower() != "where":
        print("Ошибка: Ожидается ключевое слово 'where'")
        return
    
    if len(args) == 4:
        print("Ошибка: Отсутствуют условия после 'where'")
        print("Использование: select from <таблица> where <столбец> = <значение>")
        return

    where_str = " ".join(args[4:])
    where_clause = parse_conditions(where_str)

    if where_clause is None:
        return

    for col_name in where_clause.keys():
        if col_name.lower() not in table_schema_norm:
            print(
                f"Ошибка: Столбец '{col_name}' не существует в таблице '{table_name}'"
            )
            print(f"Доступные столбцы: {', '.join(table_schema.keys())}")
            return

    try:
        converted_where = convert_where_clause(where_clause, table_schema_norm)
        where_clause = converted_where
    except ValueError as e:
        print(f"Ошибка типов в условии WHERE: {e}")
        return
    
    table_data = load_table_data(table_name)
    
    if not table_data:
        print(f"Таблица '{table_name}' пуста")
        return
    
    result_data = select(table_data, where_clause)

    if not result_data:
        print("Записи не найдены")
        return

    if table_name in metadata:
        columns = list(metadata[table_name].keys())
    else:
        columns = list(result_data[0].keys())
 
    display_table(result_data, columns)



def handle_delete(metadata, args):
    """
    Обрабатывает команду delete в формате: delete from <table> where <условия>
    """

    if len(args) < 4:
        print("Ошибка: Недостаточно аргументов для delete")
        print("Использование: delete from <имя_таблицы> where <условия>")
        return

    if args[1].lower() != "from":
        print("Ошибка: Ожидается ключевое слово 'from'")
        return

    if not validate_where_conditions(args, 4):  # начинаем с индекса 4 (после 'where')
        return
    
    table_name = args[2].lower()

    if table_name not in metadata:
        print(f"Ошибка: Таблица '{table_name}' не существует")
        return

    if args[3].lower() != "where":
        print("Ошибка: Ожидается ключевое слово 'where'")
        return

    if len(args) == 4:
        print("Ошибка: Отсутствуют условия после WHERE")
        print("Использование: delete from <таблица> where <условия>")
        return

    where_str = " ".join(args[4:])
    where_clause = parse_conditions(where_str)
    if where_clause is None:
        return

    table_schema = metadata[table_name]
    table_schema_norm = normalize_table_schema(table_schema)
    table_data = load_table_data(table_name)

    if not table_data:
        print(f"Таблица '{table_name}' пуста")
        return

    for col_name in where_clause.keys():
        if col_name.lower() not in table_schema_norm:
            print(f"Ошибка: Столбец '{col_name}' не существует в таблице '{table_name}'")
            print(f"Доступные столбцы: {', '.join(table_schema.keys())}")
            return

    try:
        converted_where = convert_where_clause(where_clause, table_schema_norm)
        where_clause = converted_where
    except ValueError as e:
        print(f"Ошибка типов в условии WHERE: {e}")
        return
    
    remaining_data, deleted_count = delete(table_data, where_clause)

    if deleted_count > 0:
        if save_table_data(table_name, remaining_data):
            print(f"Удалено записей: {deleted_count}")
        else:
            print("Ошибка при сохранении данных")
    else:
        print("Записи для удаления не найдены")


def handle_update(metadata, args):
    """
    Обрабатывает команду update в формате: update <table> set <условия> where <условия>
    """

    if len(args) < 6:
        print("Ошибка: Недостаточно аргументов для update")
        print("Использование: update <имя_таблицы> set <условия> where <условия>")
        return

    table_name = args[1].lower()
    
    
    if table_name not in metadata:
        print(f"Ошибка: Таблица '{table_name}' не существует")
        return

    if args[2].lower() != "set":
        print("Ошибка: Ожидается ключевое слово 'set'")
        return

    where_index = -1
    for i, arg in enumerate(args):
        if arg.lower() == "where":
            where_index = i
            break

    if where_index == -1:
        print("Ошибка: Ожидается ключевое слово 'where'")
        return

    if not validate_set_conditions(args, 3):  # начинаем с индекса 3 (после 'set')
        return
    
    if not validate_where_conditions(args, where_index + 1):  # начинаем после 'where'
        return

    set_str = " ".join(args[3:where_index])
    where_str = " ".join(args[where_index + 1 :])

    set_clause = parse_conditions(set_str)
    where_clause = parse_conditions(where_str)


    if set_str.strip() == "" or set_clause is None or len(set_clause) == 0:
        print("Ошибка: Отсутствуют условия для обновления после SET")
        print("Использование: update <таблица> set <столбец>=<значение> where <столбец_условия> = <значение_условия>")
        return

    if where_str.strip() == "":
        print("Ошибка: Отсутствуют условия после WHERE")
        print("Использование: update <таблица> set <столбец>=<значение> where <условия>")
        return

    if set_clause is None or where_clause is None:
        return

    table_data = load_table_data(table_name)
    table_schema = metadata[table_name]
    
    table_schema_norm = normalize_table_schema(table_schema)

    for col_name in set_clause.keys():
        if col_name.lower() not in table_schema_norm and col_name not in ('ID', 'id'):
            print(f"Ошибка: Столбец '{col_name}' не существует в таблице '{table_name}'")
            print(f"Доступные столбцы: {', '.join(table_schema.keys())}")
            return
    
    for col_name in where_clause.keys():
        if col_name.lower() not in table_schema_norm:
            print(f"Ошибка: Столбец '{col_name}' не существует в таблице '{table_name}'")
            print(f"Доступные столбцы: {', '.join(table_schema.keys())}")
            return

    try:
        converted_set = convert_where_clause(set_clause, table_schema_norm)
        set_clause = converted_set
    except ValueError as e:
        print(f"Ошибка типов в условии SET: {e}")
        return
    
    try:
        converted_where = convert_where_clause(where_clause, table_schema_norm)
        where_clause = converted_where
    except ValueError as e:
        print(f"Ошибка типов в условии WHERE: {e}")
        return


    if not table_data:
        print(f"Таблица '{table_name}' пуста")
        return
    
    updated_data, updated_count = update(table_data, set_clause, where_clause)

    if updated_count > 0:
        if save_table_data(table_name, updated_data):
            print(f"Обновлено записей: {updated_count}")
        else:
            print("Ошибка при сохранении данных")
    else:
        print("Записи для обновления не найдены")


def handle_info(metadata, args):
    """
    Обрабатывает команду info - выводит информацию о таблице
    """

    if len(args) < 2:
        print("Ошибка: Недостаточно аргументов для info")
        print("Использование: info <имя_таблицы>")
        return

    table_name = args[1].lower()

    if table_name not in metadata:
        print(f"Ошибка: Таблица '{table_name}' не существует")
        return

    table_data = load_table_data(table_name)

    print(f"Таблица: {table_name}")

    table_schema = metadata[table_name]
    columns_info = [
        f"{col_name}:{col_type}" for col_name, col_type in table_schema.items()
    ]
    print(f"Столбцы: {', '.join(columns_info)}")

    print(f"Количество записей: {len(table_data)}")

def handle_drop_table(metadata, table_name):
    """
    Обрабатывает удаление таблицы - удаляет и метаданные и данные
    """
    
    if table_name not in metadata:
        print(f"Ошибка: Таблица '{table_name}' не существует")
        return metadata

    # Удаляем файл с данными
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Файл данных '{table_name}.json' удален")
    except Exception as e:
        print(f"Ошибка при удалении файла данных: {e}")

    # Удаляем из метаданных
    new_metadata = drop_table(metadata, table_name)
    return new_metadata