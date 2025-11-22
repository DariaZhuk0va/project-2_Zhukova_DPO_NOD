import json
import prompt
import time

def handle_db_errors(func):
    """
    Декоратор для обработки ошибок базы данных.
    
    Перехватывает:
    - FileNotFoundError: файлы данных не найдены
    - PermissionError: недостаточно прав для доступа к файлам
    - KeyError: обращение к несуществующим таблицам/столбцам  
    - ValueError: ошибки валидации типов данных
    - JSONDecodeError: ошибки парсинга JSON
    - Exception: все остальные непредвиденные ошибки
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            print(
                f"Ошибка: Файл данных не найден. Возможно, база данных "
                f"не инициализирована. Детали: {e}"
                )
            return None
        except PermissionError as e:
            print(
                f"Ошибка прав доступа: Недостаточно прав для работы "
                f"с файлом. Детали: {e}"
                )
            return None
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец не найден - {e}")
            return None
        except ValueError as e:
            print(f"Ошибка валидации данных: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Ошибка формата данных: Некорректный JSON в файле. Детали: {e}")
            return None
        except Exception as e:
            print(f"Произошла непредвиденная ошибка в функции {func.__name__}: {e}")
            return None
    return wrapper

def confirm_action(action_name):
    """
    Декоратор для запроса подтверждения опасных операций.
    
    Args:
        action_name (str): Название действия для отображения в запросе подтверждения
    """
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            response = prompt.string(
                                    f'Вы уверены, что хотите выполнить '
                                    '"{action_name}"? [y/n]: '
                                    ).strip().lower()
            
            match response:
                case 'n':
                    print("Операция отменена.")
                    if func.__name__ == 'drop_table':
                        return args[0]  
                    elif func.__name__ == 'delete':
                        return args[0], -1  
                    return None
                case 'y':
                    return func(*args, **kwargs)
                case _:
                    print('Команда не распознана. Используйте y/n')
                    return wrapper(*args, **kwargs)
        return wrapper
    return decorator

def log_time(func):
    """
    Декоратор для замера времени выполнения функции.
    """
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {execution_time:.3f} секунд")
        return result
    return wrapper