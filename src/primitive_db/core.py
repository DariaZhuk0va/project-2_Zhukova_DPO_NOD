import copy

from prettytable import PrettyTable

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
        
def create_insert_function(get_next_id):
    """
    Создает функцию insert с доступом к генератору ID
    """
    
    def insert(metadata: dict, table_name: str, values: list):

        """
        Добавляет новую запись в таблицу
        """

        if table_name not in metadata:
            print(f"Ошибка: Таблица '{table_name}' не существует")
            return None
        
        table_schema = metadata[table_name]
        expected_columns = [col for col in table_schema.keys() if col != 'ID']
        
        if len(values) != len(expected_columns):
            print(f"Ошибка: Ожидается {len(expected_columns)} значений, получено {len(values)}")
            return None
        
        next_id = get_next_id(table_name)
        
        new_record = {'ID': next_id}
        for i, col_name in enumerate(expected_columns):
            value = values[i]
            col_type = table_schema[col_name]
            
            try:
                match col_type:
                    case 'int':
                        new_record[col_name] = int(value)
                    case 'bool':
                        if value.lower() in ['true', '1', 'yes']:
                            new_record[col_name] = True
                        elif value.lower() in ['false', '0', 'no']:
                            new_record[col_name] = False
                        else:
                            print(f"Ошибка: Некорректное булево значение '{value}' для столбца '{col_name}'")
                            return None
                    case 'str':  
                        new_record[col_name] = str(value)
                    case _:
                        print(f"Ошибка: Неверный тип данных для столбца '{col_name}'")
                        return None
            except ValueError:
                print(f"Ошибка: Некорректное значение '{value}' для столбца '{col_name}' типа {col_type}")
                return None
        
        return new_record
    
    return insert

def select(table_data, where_clause =  None):
    """
    Выбирает записи из таблицы с возможностью фильтрации
    """
    
    if not table_data:
        return []
    
    if where_clause is None:
        return table_data
    
    filtered_data = []
    for record in table_data:
        equally = True
        for key, value in where_clause.items():
            if key not in record or record[key] != value:
                equally = False
                break
        if equally:
            filtered_data.append(record)
    
    return filtered_data

def update(table_data, set_clause, where_clause = None):
    """
    Обновляет записи в таблице
    """
    
    updated_data = table_data.copy()
    updated_count = 0
    
    for i, record in enumerate(updated_data):
        equally = True
        if where_clause:
            for key, value in where_clause.items():
                if key not in record or record[key] != value:
                    equally = False
                    break
        
        if equally:
            for key, value in set_clause.items():
                if key in record and key != 'ID':  # ID нельзя изменять
                    if isinstance(record[key], bool):
                        if value.lower() in ['true', '1', 'yes']:
                            updated_data[i][key] = True
                        else:
                            updated_data[i][key] = False
                    elif isinstance(record[key], int):
                        updated_data[i][key] = int(value)
                    else:
                        updated_data[i][key] = str(value)
            updated_count += 1
    
    return updated_data, updated_count

def delete(table_data, where_clause=None):
    """
    Удаляет записи из таблицы
    """

    if where_clause is None:
        return [], len(table_data)
    
    remaining_data = []
    deleted_count = 0
    
    for record in table_data:
        equally = True
        for key, value in where_clause.items():
            if key not in record or record[key] != value:
                equally = False
                break
        
        if not equally:
            remaining_data.append(record)
        else:
            deleted_count += 1
    
    return remaining_data, deleted_count

def display_table(data, columns):
    """
    Отображает данные в виде красивой таблицы
    """
    
    if not data:
        print("Нет данных для отображения")
        return
    
    table = PrettyTable()
    table.field_names = columns
    
    for record in data:
        row = [record.get(col, '') for col in columns]
        table.add_row(row)
    
    print(table)