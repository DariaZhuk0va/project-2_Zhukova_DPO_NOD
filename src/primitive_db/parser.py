import shlex

def parse_conditions(condition_str):
    """
    Парсит условия в формате 'key1 = value1, key2 = value2'
    """
    
    if not condition_str:
        return None
    
    try:
        conditions = {}
        parts = shlex.split(condition_str)
        
        i = 0
        while i < len(parts):
            if i + 2 < len(parts) and parts[i + 1] == '=':
                key = parts[i]
                raw_value = parts[i + 2]
                
                value = parse_value(raw_value)
                conditions[key] = value
                
                i += 3
                
                if i < len(parts) and parts[i] == ',':
                    i += 1
            else:
                print("Ошибка: Некорректный формат условий")
                print("Используйте: key1 = value1, key2 = value2")
                return None
        
        return conditions
    except Exception as e:
        print(f"Ошибка при разборе условий: {e}")
        return None

def parse_value(raw_value):
    """
    Парсит значение с автоматическим определением типа
    """
    
    if (raw_value.startswith('"') and raw_value.endswith('"')) or (raw_value.startswith("'") and raw_value.endswith("'")):
        return raw_value[1:-1]
    
    # Пробуем преобразовать в целое число
    try:
        return int(raw_value)
    except ValueError:
        pass
    
    # Пробуем преобразовать в булево значение
    if raw_value.lower() in ['true', 'yes', '1']:
        return True
    elif raw_value.lower() in ['false', 'no', '0']:
        return False
    
    # Если ничего не подошло - возвращаем как строку
    return raw_value