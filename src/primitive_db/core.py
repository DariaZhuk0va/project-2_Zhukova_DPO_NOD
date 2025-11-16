import copy


def create_table(metadata, table_name, columns):
    """
    Создает новую таблицу в метаданных.

    Args:
        metadata (dict): Текущие метаданные базы данных
        table_name (str): Имя таблицы для создания
        columns (list): Список столбцов в формате ['столбец:тип', ...]

    Returns:
        dict: Обновленные метаданные или исходные метаданные в случае ошибки
    """
    if table_name in metadata:
        print(f"Ошибка: Таблица '{table_name}' уже существует")
        return metadata

    new_metadata = copy.deepcopy(metadata)
    table_columns = {"ID": "int"}

    for col_name, col_type in columns.items():
        col_type = col_type.lower().strip()

        if col_type not in ["int", "str", "bool"]:
            print(
                f"Ошибка: Неподдерживаемый тип данных '{col_type}' "
                f"для столбца '{col_name}'. "
                f"Поддерживаемые типы: int, str, bool"
            )
            return metadata

        if col_name in table_columns:
            print(f"Ошибка: Столбец с именем '{col_name}' уже существует в таблице")
            return metadata

        table_columns[col_name] = col_type

    new_metadata[table_name] = table_columns
    print(f"Таблица '{table_name}' успешно создана")
    return new_metadata


def drop_table(metadata, table_name):
    """
    Удаляет таблицу из метаданных.

    Args:
        metadata (dict): Текущие метаданные базы данных
        table_name (str): Имя таблицы для удаления

    Returns:
        dict: Обновленные метаданные
    """

    if table_name not in metadata:
        print(f"Ошибка: Таблица '{table_name}' не существует")
        return metadata

    del metadata[table_name]
    print(f"Таблица '{table_name}' успешно удалена")
    return metadata

def list_tables(metadata):
    """
    Показывает список всех таблиц в базе данных.
    
    Args:
        metadata (dict): Метаданные базы данных
    """
    if not metadata:
        print("В базе данных нет таблиц.")
        return
    
    print("Таблицы в базе данных:")
    for i, table_name in enumerate(metadata.keys(), 1):
        print(f"{i}. {table_name}")
        
