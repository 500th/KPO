import os


def find_empty_folders(root_path):
    empty_folders = []

    for current_path, folders, files in os.walk(root_path):
        if not folders and not files:
            empty_folders.append(current_path)

    return empty_folders