import shlex

def parse_conditions(condition_str):
    """
    Парсит условия в формате 'key1 = value1, key2 = value2'
    """
    if not condition_str:
        return None
    
    try:
        conditions = {}
        conditions_list = split_by_commas(condition_str)
        
        for condition in conditions_list:
            condition = condition.strip()
            if '=' in condition:
                parts = condition.split('=', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    raw_value = parts[1].strip()
                    conditions[key] = raw_value
                else:
                    print(f"Ошибка: Некорректное условие '{condition}'")
                    return None
            else:
                print(f"Ошибка: Отсутствует знак '=' в условии '{condition}'")
                return None
       
        return conditions
    except Exception as e:
        print(f"Ошибка при разборе условий: {e}")
        return None

def split_by_commas(text):
    """
    Делит строку по запятым, игнорируя запятые внутри кавычек
    """
    
    parts = []
    current_part = []
    in_quotes = False
    quote_char = None
  
    for char in text:
        if char in ['"', "'"]:
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
            current_part.append(char)
        elif char == ',' and not in_quotes:
            parts.append(''.join(current_part).strip())
            current_part = []
        else:
            current_part.append(char)
    
    if current_part:
        parts.append(''.join(current_part).strip())
    
    return parts

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
            
            # Если ничего не подошло - строка
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
        # Ищем паттерн: столбец = значение
        if i + 2 < len(args) and args[i + 1] == '=':
            column = args[i]
            value_start = i + 2
            
            # Ищем конец значения (до следующего оператора = или конца)
            j = value_start
            while j < len(args):
                # Если нашли следующий оператор =, значит текущее значение закончилось
                if j + 1 < len(args) and args[j + 1] == '=':
                    break
                j += 1
            
            # Если значение состоит из нескольких слов (без кавычек) - ошибка
            if j > value_start + 1:
                original_value = ' '.join(args[value_start:j])
                print("Ошибка: Обнаружены пробелы в значении условия WHERE")
                print("Если значение содержит пробелы, заключите его в кавычки:")
                print(f"Используйте: {column} = \"{original_value}\"")
                return False
            
            # Переходим к следующему условию
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
        # Ищем паттерн: столбец = значение
        if i + 2 < len(args) and args[i + 1] == '=':
            column = args[i]
            value_start = i + 2
            
            # Ищем конец значения (до следующего оператора =, WHERE или конца)
            j = value_start
            while j < len(args):
                # Если нашли следующий оператор = или WHERE, значит текущее значение закончилось
                if j + 1 < len(args) and args[j + 1] == '=':
                    break
                if args[j].lower() == 'where':
                    break
                j += 1
            
            # Если значение состоит из нескольких слов (без кавычек) - ошибка
            if j > value_start + 1:
                original_value = ' '.join(args[value_start:j])
                print("Ошибка: Обнаружены пробелы в значении условия SET")
                print("Если значение содержит пробелы, заключите его в кавычки:")
                print(f"Используйте: {column} = \"{original_value}\"")
                return False
            
            # Переходим к следующему условию
            i = j
        else:
            i += 1
    
    return True