import os
import uuid
import mimetypes
import gdown

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


def download_google_drive_file(url: str):
    unique_name = str(uuid.uuid4())

    downloaded_file = gdown.download(
        url=url,
        output=os.path.join(TEMP_DIR, unique_name),
        quiet=False,
        fuzzy=True
    )

    if not downloaded_file:
        raise Exception(
            "Не удалось скачать файл. Убедитесь, что доступ открыт для всех, у кого есть ссылка."
        )

    if not os.path.exists(downloaded_file):
        raise Exception("Файл был скачан некорректно")

    mime_type, guessed_extension = mimetypes.guess_type(downloaded_file)

    if guessed_extension is None:
        possible_extensions = [
            ".mp3", ".wav", ".ogg", ".m4a",
            ".mp4", ".mov", ".avi", ".mkv"
        ]

        for ext in possible_extensions:
            test_path = downloaded_file + ext
            try:
                os.rename(downloaded_file, test_path)
                downloaded_file = test_path
                guessed_extension = ext
                break
            except Exception:
                continue

    file_size_bytes = os.path.getsize(downloaded_file)
    file_size_gb = file_size_bytes / (1024 ** 3)

    return downloaded_file, file_size_gb