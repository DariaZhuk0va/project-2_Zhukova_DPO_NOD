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