import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from folder_scanner import find_empty_folders
from folder_cleaner import delete_empty_folders
from file_generator import generate_file

def create_interface():
    root = tk.Tk()
    root.title("Утилита файловой системы")
    root.geometry("700x450")

    tabs = ttk.Notebook(root)
    tabs.pack(fill="both", expand=True)

    cleaner_tab = ttk.Frame(tabs, padding=10)
    generator_tab = ttk.Frame(tabs, padding=10)
    tabs.add(cleaner_tab, text="Очистка папок")
    tabs.add(generator_tab, text="Генератор файлов")

    path_var = tk.StringVar()

    def choose_folder():
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)

    def scan_folders():
        path = path_var.get().strip()

        if not os.path.isdir(path):
            messagebox.showerror("Ошибка", "Выберите существующую папку.")
            return

        folder_list.delete(0, tk.END)

        for folder in find_empty_folders(path):
            if os.path.normcase(os.path.abspath(folder)) != os.path.normcase(os.path.abspath(path)):
                folder_list.insert(tk.END, folder)

        if folder_list.size() == 0:
            messagebox.showinfo("Результат", "Пустые вложенные папки не найдены.")

    def delete_selected():
        indices = folder_list.curselection()

        if not indices:
            messagebox.showwarning("Удаление", "Сначала выберите папки в списке.")
            return

        selected = [folder_list.get(index) for index in indices]

        confirmed = messagebox.askyesno(
            "Подтверждение удаления",
            f"Удалить выбранные папки ({len(selected)})?\n"
            "Они не попадут в корзину."
        )
        if not confirmed:
            return

        deleted, errors = delete_empty_folders(path_var.get().strip(), selected)

        for index in reversed(indices):
            if folder_list.get(index) in deleted:
                folder_list.delete(index)

        messagebox.showinfo("Результат", f"Удалено папок: {len(deleted)}")

        if errors:
            details = "\n".join(f"{path}: {error}" for path, error in errors)
            messagebox.showwarning("Не удалось удалить", details)

    ttk.Label(cleaner_tab, text="Папка для проверки:").pack(anchor="w")
    ttk.Entry(cleaner_tab, textvariable=path_var).pack(fill="x", pady=5)
    ttk.Button(cleaner_tab, text="Выбрать папку", command=choose_folder).pack(anchor="w")
    ttk.Button(cleaner_tab, text="Найти пустые папки", command=scan_folders).pack(anchor="w", pady=10)

    folder_list = tk.Listbox(cleaner_tab, selectmode=tk.EXTENDED)
    folder_list.pack(fill="both", expand=True)
    ttk.Button(
        cleaner_tab,
        text="Удалить выбранные",
        command=delete_selected
    ).pack(anchor="e", pady=10)

    # Создание файлов
    output_folder_var = tk.StringVar()
    file_name_var = tk.StringVar()
    file_size_var = tk.StringVar(value="1")
    unit_var = tk.StringVar(value="КБ")
    content_var = tk.StringVar(value="Нули")

    def choose_output_folder():
        folder = filedialog.askdirectory()
        if folder:
            output_folder_var.set(folder)

    def create_file():
        try:
            size = int(file_size_var.get())
            path = generate_file(
                output_folder_var.get().strip(),
                file_name_var.get().strip(),
                size,
                unit_var.get(),
                content_var.get()
            )
        except (ValueError, OSError) as error:
            messagebox.showerror("Ошибка создания файла", str(error))
            return

        messagebox.showinfo("Готово", f"Файл создан:\n{path}")

    ttk.Label(generator_tab, text="Папка для сохранения:").pack(anchor="w")
    ttk.Entry(generator_tab, textvariable=output_folder_var).pack(fill="x", pady=5)
    ttk.Button(
        generator_tab, text="Выбрать папку", command=choose_output_folder
    ).pack(anchor="w")

    ttk.Label(generator_tab, text="Имя файла:").pack(anchor="w", pady=(15, 0))
    ttk.Entry(generator_tab, textvariable=file_name_var).pack(fill="x", pady=5)

    ttk.Label(generator_tab, text="Размер файла:").pack(anchor="w", pady=(10, 0))
    ttk.Entry(generator_tab, textvariable=file_size_var).pack(fill="x", pady=5)

    ttk.Label(generator_tab, text="Единица измерения:").pack(anchor="w")
    ttk.Combobox(
        generator_tab, textvariable=unit_var,
        values=("КБ", "МБ", "ГБ"), state="readonly"
    ).pack(fill="x", pady=5)

    ttk.Label(generator_tab, text="Содержимое файла:").pack(anchor="w")
    ttk.Combobox(
        generator_tab, textvariable=content_var,
        values=("Нули", "Случайные данные"), state="readonly"
    ).pack(fill="x", pady=5)

    ttk.Button(
        generator_tab, text="Создать файл", command=create_file
    ).pack(anchor="e", pady=15)

    root.mainloop()
