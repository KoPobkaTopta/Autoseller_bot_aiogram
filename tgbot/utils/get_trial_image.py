import os
from typing import Generator


async def get_text_from_file(folder: str) -> Generator[str, None, None]:
    """
    Асинхронно считывает текст из файлов .txt в указанной папке.

    Args:
        folder (str): Путь к папке с файлами.

    Yields:
        str: Текст из файла.
    """
    for root, _, files in os.walk(folder):
        for filename in sorted(files):
            if filename.endswith('.txt'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    yield file.read()

