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


async def formatting_items(item: dict) -> str:
    """Форматирует данные о товаре."""
    name = item.get('name', 'Название не указано')
    brand = item.get('oem_brand', 'Не указан')
    oem_num = item.get('oem_num', 'Не указан')
    price = item.get('price', 'Не указана')
    count = item.get('count', 0)
    unit = item.get('unit', 'шт')
    chel = item.get('count_chel', 0)
    ekb = item.get('count_ekb', 0)
    message = (
            f"📦 <b>{name}</b>\n"
            f"🏢 <b>Производитель:</b> {brand}\n"
            f"🔢 <b>Артикул:</b> {oem_num}\n"
            f"🏷️ <b>Цена:</b> {price} руб.\n"
            f"📊 <b>Количество на складах:</b> {count} "
            f"{unit} (Челябинск: "
            f"{chel} {unit}, "
            f"Екатеринбург: {ekb} "
            f"{unit})\n\n"
    )
    return message
