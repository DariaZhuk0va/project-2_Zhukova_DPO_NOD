import json
import os

from .constants import DATA_DIR, METADATA_FILE
from .decorators import handle_db_errors


@handle_db_errors
def ensure_data_dir():
    """
    Создает директорию data если она не существует
    """

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
        print(f"Директория '{DATA_DIR}' создана")
    return True

@handle_db_errors
def initialize_database():
    """
    Инициализирует базу данных - создает необходимые файлы если их нет
    """
    ensure_data_dir()
    
    if not os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=2)
        print(f"Файл метаданных '{METADATA_FILE}' создан")
    
    return True

@handle_db_errors
def load_metadata(filepath):
    """
    Загружает данные из JSON-файла.
    Если файл не найден, возвращает пустой словарь {}.
    """
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read().strip()
        if not content:
            return {}
        return json.loads(content)

@handle_db_errors
def save_metadata(filepath, data):
    """
    Сохраняет переданные данные в JSON-файл
    """
    
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        return True

@handle_db_errors
def load_table_data(table_name):
    """
    Загружает данные таблицы из файла
    """
    
    ensure_data_dir()
    
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")

    try:
        with open(filepath, 'r', encoding = 'utf-8') as file:
            content = file.read().strip()
            if not content:
                return []
            data = list(json.loads(content))
            return data
    
    except FileNotFoundError:
        with open(filepath, 'w', encoding = 'utf-8') as file:
            json.dump({}, file, ensure_ascii = False, indent = 2)
        print(f"Файл метаданных '{filepath}' создан")
        return []
    
    except json.JSONDecodeError as e:
        print(f"Ошибка: Файл {filepath} содержит некорректный JSON: {e}")
        return []
    
@handle_db_errors
def save_table_data(table_name, data):
    """
    Сохраняет данные таблицы в файл
    """
    
    ensure_data_dir()
    
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    return True

@handle_db_errors    
def get_next_id(table_name):
    """
    Генерирует следующий ID для таблицы
    """
    
    START_ID = 1
    table_data = load_table_data(table_name)
    if table_data:
        existing_ids = {record['ID'] for record in table_data}
        next_id = max(existing_ids) + 1
        
        return next_id
    else:
        return START_ID

@handle_db_errors     
def normalize_table_schema(table_schema):
    """
    Приводит все имена столбцов в схеме таблицы к нижнему регистру
    """
    normalized_schema = {}
    for col_name, col_type in table_schema.items():
        normalized_schema[col_name.lower()] = col_type
    return normalized_schema

@handle_db_errors   
def create_cacher():
    """
    Создает замыкание для кэширования результатов.
    
    Returns:
        Функция cache_result(key, value_func) для кэширования
    """
    
    cache = {} 
    
    def cache_result(key, value_func):
        """
        Кэширует результат выполнения функции.
        
        Args:
            key: Ключ для кэша (должен быть хэшируемым)
            value_func: Функция для получения данных, если их нет в кэше
            
        Returns:
            Результат выполнения value_func или значение из кэша
        """

        if key in cache:
            return cache[key]
        else:
            result = value_func()
            cache[key] = result
            return result
    
    def invalidate_table_cache(table_name):
        """
        Удаляет из кэша все записи, связанные с указанной таблицей
        """
        keys_to_remove = []
        for key in cache.keys():
            if (key.startswith(f"select_{table_name}_") or
                key == f"select_all_{table_name}"):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del cache[key]
           
    def get_cache_stats():
        """
        Возвращает статистику кэша
        """
        return {
            'total_entries': len(cache),
            'keys': list(cache.keys())
        }
    
    return cache_result, invalidate_table_cache, get_cache_stats

# Глобальные кэшеры
select_cacher, invalidate_table_cache, get_cache_stats = create_cacher()

