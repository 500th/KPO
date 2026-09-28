import os
import shutil


def generate_file(folder, name, size, unit, content_type):
    if not os.path.isdir(folder):
        raise ValueError("Папка для сохранения не существует")

    if not name or os.path.basename(name) != name:
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

    if os.path.exists(path):
        raise FileExistsError("Файл с таким именем уже существует")

    if shutil.disk_usage(folder).free < size_bytes:
        raise OSError("Недостаточно свободного места")

    created = False
    try:
        with open(path, "xb") as output:
            created = True
            remaining = size_bytes

            while remaining > 0:
                block_size = min(1024 * 1024, remaining)

                if content_type == "Нули":
                    data = bytes(block_size)
                else:
                    data = os.urandom(block_size)

                output.write(data)
                remaining -= block_size
    except OSError:
        if created:
            os.remove(path)
        raise

    return path