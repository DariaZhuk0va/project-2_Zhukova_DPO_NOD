import json


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
    print(f"DEBUG: save_metadata вызван с filepath='{filepath}'")
    print(f"DEBUG: Данные для сохранения: {data}")
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            print(f"Метаданные успешно сохранены в '{filepath}'")
    except FileNotFoundError:
        print(f"Ошибка: Директория для файла '{filepath}' не существует")
        print("Создайте директорию вручную или укажите корректный путь")
    except PermissionError:
        print(f"Ошибка: Нет прав на запись в файл '{filepath}'")
    except Exception as e:
        print(f"Ошибка при сохранении метаданных: {e}")
