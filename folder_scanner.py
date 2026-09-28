import os


def find_empty_folders(root_path, excluded_paths=()):
    excluded = {
        os.path.normcase(os.path.abspath(path))
        for path in excluded_paths
    }
    empty_folders = []
    empty_paths = set()
    visited = []

    def handle_error(error):
        raise error

    for current_path, folders, files in os.walk(
        root_path, topdown=True, onerror=handle_error
    ):
        all_folders = folders[:]

        folders[:] = [
            name for name in folders
            if os.path.normcase(
                os.path.abspath(os.path.join(current_path, name))
            ) not in excluded
        ]

        visited.append((current_path, all_folders, files))

    for current_path, folders, files in reversed(visited):
        children_are_empty = all(
            os.path.normcase(
                os.path.abspath(os.path.join(current_path, name))
            ) in empty_paths
            for name in folders
        )

        if not files and children_are_empty:
            empty_folders.append(current_path)
            empty_paths.add(
                os.path.normcase(os.path.abspath(current_path))
            )

    return empty_folders