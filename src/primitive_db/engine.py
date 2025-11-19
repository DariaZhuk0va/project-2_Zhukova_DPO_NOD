import shlex

import prompt

from .core import create_table, drop_table, list_tables, create_insert_function, select, update, delete, display_table
from .utils import load_metadata, save_metadata, METADATA_FILE, load_table_data, save_table_data, get_next_id
from .parser import parse_conditions


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
                    new_metadata = drop_table(metadata, table_name)
                    
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
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию")
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def handle_insert(metadata, args):
    """
    Обрабатывает команду insert в формате: insert into <table> values (val1, val2, ...)
    """
    
    if len(args) < 4:
        print("Ошибка: Недостаточно аргументов для insert")
        print("Использование: insert into <имя_таблицы> values (<значение1>, <значение2>, ...)")
        return
    
    if args[1].lower() != 'into':
        print("Ошибка: Ожидается ключевое слово 'into'")
        print("Использование: insert into <имя_таблицы> values (<значение1>, <значение2>, ...)")
        return
    
    table_name = args[2]
    
    if args[3].lower() != 'values':
        print("Ошибка: Ожидается ключевое слово 'values'")
        return
    
    values_str = ' '.join(args[4:])
    
    if values_str.startswith('(') and values_str.endswith(')'):
        values_str = values_str[1:-1]
    
    try:
        values = shlex.split(values_str.replace(',', ' '))
    except Exception as e:
        print(f"Ошибка при разборе значений: {e}")
        return
    
    insert = create_insert_function(get_next_id)
    new_record = insert(metadata, table_name, values)
    
    if new_record:
        table_data = load_table_data(table_name)
        
        table_data.append(new_record)
        
        if save_table_data(table_name, table_data):
            print(f"Запись успешно добавлена с ID: {new_record['ID']}")
        else:
            print("Ошибка при сохранении данных")

def handle_select(metadata, args):
    """
    Обрабатывает команду select в формате: select from <table> [where условия]
    """
    
    if len(args) < 3:
        print("Ошибка: Недостаточно аргументов для select")
        print("Использование: select from <имя_таблицы> [where условия]")
        return
    
    if args[1].lower() != 'from':
        print("Ошибка: Ожидается ключевое слово 'from'")
        return
    
    table_name = args[2]
    
    where_clause = None
    if len(args) > 3:
        if args[3].lower() != 'where':
            print("Ошибка: Ожидается ключевое слово 'where'")
            return
        
        where_str = ' '.join(args[4:])
        where_clause = parse_conditions(where_str)
        if where_clause is None:  
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
    
    if args[1].lower() != 'from':
        print("Ошибка: Ожидается ключевое слово 'from'")
        return
    
    table_name = args[2]
    
    if args[3].lower() != 'where':
        print("Ошибка: Ожидается ключевое слово 'where'")
        return
    
    where_str = ' '.join(args[4:])
    where_clause = parse_conditions(where_str)
    if where_clause is None: 
        return
    
    table_data = load_table_data(table_name)
    
    if not table_data:
        print(f"Таблица '{table_name}' пуста")
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
    
    table_name = args[1]
    
    if args[2].lower() != 'set':
        print("Ошибка: Ожидается ключевое слово 'set'")
        return
    
    where_index = -1
    for i, arg in enumerate(args):
        if arg.lower() == 'where':
            where_index = i
            break
    
    if where_index == -1:
        print("Ошибка: Ожидается ключевое слово 'where'")
        return
    
    set_str = ' '.join(args[3:where_index])
    where_str = ' '.join(args[where_index + 1:])
    
    set_clause = parse_conditions(set_str)
    where_clause = parse_conditions(where_str)
    
    if set_clause is None or where_clause is None:
        return
    
    table_data = load_table_data(table_name)
    
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
    
    table_name = args[1]
    
    if table_name not in metadata:
        print(f"Ошибка: Таблица '{table_name}' не существует")
        return
    
    table_data = load_table_data(table_name)
    
    print(f"Таблица: {table_name}")
    
    table_schema = metadata[table_name]
    columns_info = [f"{col_name}:{col_type}" for col_name, col_type in table_schema.items()]
    print(f"Столбцы: {', '.join(columns_info)}")
    
    print(f"Количество записей: {len(table_data)}")
