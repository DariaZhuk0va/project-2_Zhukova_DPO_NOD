from .decorators import handle_db_errors


@handle_db_errors
def parse_values(values_list):
    """
    Парсит значения в формате VALUES (value1, value2, value3)
    Возвращает список значений
    """
   
    if not values_list:
        return []
    
    result_values_list =[]
    for value in values_list:
        
        value = value.strip()
        if value.startswith('('):
            value = value[1:].strip()
        if value.endswith(')'):
            value = value[:-1].strip()
        if value.endswith(','):
            value = value[:-1].strip()
        result_values_list.append(value)

    return result_values_list

@handle_db_errors
def parse_conditions(set_list):
    """
    Парсит условия SET в формате [col1, =, value1, col2, =, value2]
    Возвращает словарь {col: value}
    """
    if not set_list:
        return {}

    conditions = {}
    for i, item in enumerate(set_list):
        set_part = i % 3
        EQUAL_INDEX = 1
        if set_part == EQUAL_INDEX and item != '=':
            print(f"Ошибка: Отсутствует знак '=' в условии после {set_list[i - 1]}")
            return {}
        
        if set_part == 0:
            if len(set_list) - i < 3:
                return {} 
            col = item.strip()
            value = set_list[i + 2].strip()
            if (i + 2 != len(set_list) - 1):
                if value.endswith(','):
                    value = value[:-1].strip()
                else:
                    print('Ошибка: Между условиями отсутсвует запятая')
                    return {} 
            else:
                if value.endswith(','):
                    print('Ошибка: После условий лишняя запятая')
                    return {} 
            conditions[col] = value

    return conditions

def convert_value(value, expected_type = None):
    """
    Преобразует значение в указанный тип или определяет тип автоматически.
    
    Args:
        value: Исходное значение (обычно строка)
        expected_type: Ожидаемый тип ('int', 'str', 'bool') или None для автоопределения
    
    Returns:
        Преобразованное значение нужного типа
    """
   
    if value is None:
        return None
    
    if not isinstance(value, str):
        value = str(value)
   
    match expected_type: 
        case 'int':
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"Невозможно преобразовать '{value}' в int")
    
        case 'bool':
            if value.lower() in ['true', '1', 'yes', 'on']:
                return True
            elif value.lower() in ['false', '0', 'no', 'off']:
                return False
            else:
                raise ValueError(f"Невозможно преобразовать '{value}' в bool")
    
        case 'str':
            return value
        
        case _:
            try:
                return int(value)
            except ValueError:
                pass
            
            if value.lower() in ['true', '1', 'yes', 'on']:
                return True
            elif value.lower() in ['false', '0', 'no', 'off']:
                return False
            
            return value

def convert_where_clause(where_clause, table_schema):
    """
    Преобразует условия WHERE согласно типам столбцов таблицы.
    
    Args:
        where_clause: Словарь условий {'col': 'value'}
        table_schema: Схема таблицы {'col_name': 'type'}
    
    Returns:
        Словарь с преобразованными значениями
    """
    if where_clause is None:
        return None
    
    converted = {}
    for col_name, raw_value in where_clause.items():
        if col_name in table_schema:
            expected_type = table_schema[col_name]
            try:
                converted[col_name] = convert_value(raw_value, expected_type)
            except ValueError as e:
                raise ValueError(str(e))        
        else:
            converted[col_name] = convert_value(raw_value)
    return converted

def validate_where_conditions(args, start_index):
    """
    Проверяет условия WHERE на наличие пробелов в значениях без кавычек.
    """
    i = start_index

    while i < len(args):
        if i + 2 < len(args) and args[i + 1] == '=':
            column = args[i]
            value_start = i + 2
            
            j = value_start
            while j < len(args):
                if j + 1 < len(args) and args[j + 1] == '=':
                    break
                j += 1
            
            if j > value_start + 1:
                original_value = ' '.join(args[value_start:j])
                print("Ошибка: Обнаружены пробелы в значении условия WHERE")
                print("Если значение содержит пробелы, заключите его в кавычки:")
                print(f"Используйте: {column} = \"{original_value}\"")
                return False
            
            i = j
        else:
            i += 1
    
    return True

def validate_set_conditions(args, start_index):
    """
    Проверяет условия SET на наличие пробелов в значениях без кавычек.
    """
    i = start_index
    while i < len(args):
        if i + 2 < len(args) and args[i + 1] == '=':
            column = args[i]
            value_start = i + 2
        
            j = value_start
            while j < len(args):
                
                if j + 1 < len(args) and args[j + 1] == '=':
                    break
                if args[j].lower() == 'where':
                    break
                j += 1
            
            if j > value_start + 1:
                original_value = ' '.join(args[value_start:j])
                print("Ошибка: Обнаружены пробелы в значении условия SET")
                print("Если значение содержит пробелы, заключите его в кавычки:")
                print(f"Используйте: {column} = \"{original_value}\"")
                return False
            
            i = j
        else:
            i += 1
    
    return True

