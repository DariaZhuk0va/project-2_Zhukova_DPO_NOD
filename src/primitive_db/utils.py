import json
import os

# Константы
METADATA_FILE = 'db_meta.json'
DATA_DIR = 'data'

def ensure_data_dir():
    """Создает директорию data если она не существует"""

    os.makedirs(DATA_DIR, exist_ok=True)

def load_metadata(filepath):
    """
    Загружает данные из JSON-файла.
    Если файл не найден, возвращает пустой словарь {}.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                return {}
            return json.loads(content)

    except FileNotFoundError:
        return {}

    except Exception as e:
        print(f"Ошибка при загрузке метаданных из {filepath}: {e}")
        return {}


def save_metadata(filepath, data):
    """
    Сохраняет переданные данные в JSON-файл

    """
    
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except FileNotFoundError:
        print(f"Ошибка: Директория для файла '{filepath}' не существует")
        print("Создайте директорию вручную или укажите корректный путь")
    except PermissionError:
        print(f"Ошибка: Нет прав на запись в файл '{filepath}'")
    except Exception as e:
        print(f"Ошибка при сохранении метаданных: {e}")

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
            return json.loads(content)
    
    except FileNotFoundError:
        return []
    
    except json.JSONDecodeError:
        print(f"Ошибка: Файл {filepath} содержит некорректный JSON")
        return []
    
    except Exception as e:
        print(f"Ошибка при загрузке данных таблицы {table_name}: {e}")
        return []

def save_table_data(table_name, data):
    """
    Сохраняет данные таблицы в файл
    """
    
    ensure_data_dir()
    
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return True
    
    except Exception as e:
        print(f"Ошибка при сохранении данных таблицы {table_name}: {e}")
        return False

def get_next_id(table_name):
    """
    Генерирует следующий ID для таблицы
    """
    
    table_data = load_table_data(table_name)
    if table_data:
        return max(record['ID'] for record in table_data) + 1
    else:
        return 1