import os


def find_empty_folders(root_path):
    empty_folders = []
    empty_paths = set()

    for current_path, folders, files in os.walk(root_path, topdown=False):
        if not files and all(
            os.path.join(current_path, folder) in empty_paths
            for folder in folders
        ):
            empty_folders.append(current_path)
            empty_paths.add(current_path)

    return empty_folders