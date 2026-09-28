import os


def delete_empty_folders(root_path, selected_folders):
    root = os.path.normcase(os.path.abspath(root_path))
    deleted = []
    errors = []

    folders = sorted(
        set(selected_folders),
        key=lambda path: path.count(os.sep),
        reverse=True
    )

    for folder in folders:
        path = os.path.abspath(folder)
        normalized_path = os.path.normcase(path)

        try:
            if (
                normalized_path == root
                or os.path.commonpath([root, normalized_path]) != root
            ):
                errors.append((path, "Нельзя удалить исходную папку или папку вне неё"))
                continue

            os.rmdir(path)
            deleted.append(path)
        except (OSError, ValueError) as error:
            errors.append((path, str(error)))

    return deleted, errors