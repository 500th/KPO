import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from folder_scanner import find_empty_folders
from folder_cleaner import delete_empty_folders


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

    ttk.Label(generator_tab, text="Генератор файлов добавим следующим этапом.").pack()

    root.mainloop()
