import shlex

import prompt

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata


def run():
    """
    Главная функция с основным циклом программы.
    """

    print("Добро пожаловать в модуль 'База данных'!\n")
    print("Введите 'help' для просмотра доступных команд.")
    print("Введите 'exit' для выхода из программы.")

    while True:

        METADATA_FILE = "db_meta.json"
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

                    if new_metadata != metadata:
                        save_metadata(METADATA_FILE, new_metadata)

                case "list_tables":
                    list_tables(metadata)

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

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")
