import json
import os

from .decorators import handle_db_errors

# Константы
METADATA_FILE = 'db_meta.json'
DATA_DIR = 'data'

@handle_db_errors
def ensure_data_dir():
    """
    Создает директорию data если она не существует
    """

    def _ensure_data_dir():
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
            print(f"Директория '{DATA_DIR}' создана")
        return True
    return _ensure_data_dir()

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
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                return []
            data = json.loads(content)
            return data
    
    except FileNotFoundError:
        # Для новой таблицы возвращаем пустой список вместо ошибки
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
    
def get_next_id(table_name):
    """
    Генерирует следующий ID для таблицы
    """
    
    table_data = load_table_data(table_name)
    if table_data:
        existing_ids = {record['ID'] for record in table_data}
        next_id = max(existing_ids) + 1
        
        return next_id
    else:
        return 1
    
def normalize_table_schema(table_schema):
    """
    Приводит все имена столбцов в схеме таблицы к нижнему регистру
    """
    normalized_schema = {}
    for col_name, col_type in table_schema.items():
        normalized_schema[col_name.lower()] = col_type
    return normalized_schema