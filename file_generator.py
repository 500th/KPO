import os
import shutil
import tempfile


def generate_file(
    folder, name, size, unit, content_type,
    overwrite=False, progress_callback=None, cancel_event=None):

    if not name or name in (".", "..") or os.path.basename(name) != name:
        raise ValueError("Укажите корректное имя файла")

    if size <= 0:
        raise ValueError("Размер должен быть больше нуля")

    units = {"КБ": 1024, "МБ": 1024 ** 2, "ГБ": 1024 ** 3}
    if unit not in units:
        raise ValueError("Неизвестная единица измерения")

    if content_type not in ("Нули", "Случайные данные"):
        raise ValueError("Неизвестный тип содержимого")

    size_bytes = size * units[unit]
    path = os.path.join(folder, name)

    if os.path.exists(path) and not overwrite:
        raise FileExistsError("Файл с таким именем уже существует")

    if shutil.disk_usage(folder).free < size_bytes:
        raise OSError("Недостаточно свободного места")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=folder, prefix=".kpo_", delete=False
        ) as output:
            temp_path = output.name
            remaining = size_bytes

            while remaining > 0:
                if cancel_event is not None and cancel_event.is_set():
                    raise InterruptedError("Создание файла отменено")
                block_size = min(1024 * 1024, remaining)
                data = (
                    bytes(block_size)
                    if content_type == "Нули"
                    else os.urandom(block_size)
                )
                output.write(data)
                remaining -= block_size
                if progress_callback is not None:
                    progress_callback(size_bytes - remaining, size_bytes)

        if os.path.exists(path) and not overwrite:
            raise FileExistsError("Файл с таким именем уже существует")
        if cancel_event is not None and cancel_event.is_set():
            raise InterruptedError("Создание файла отменено")
        os.replace(temp_path, path)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    return path