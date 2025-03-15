def load_file(file_path):
    """Загружает содержимое текстового файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        error_msg = f"Файл {file_path} не найден."
        return error_msg
    except Exception as e:
        error_msg = f"Произошла ошибка: {e}"
        return error_msg
