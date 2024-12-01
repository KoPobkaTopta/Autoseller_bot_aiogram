async def get_file_content(file_path: str) -> str:
    """
    Асинхронно читает содержимое текстового файла.

    Args:
        file_path (str): Путь к текстовому файлу.

    Returns:
        str: Содержимое файла или пустая строка, если файл не удалось прочитать.
    """
    try:
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
            return await file.read()
    except Exception as e:
        logging.error(f"Ошибка чтения файла {file_path}: {e}")
        return ""
