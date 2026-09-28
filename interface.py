import os
import queue
import threading
import tkinter as tk

from tkinter import filedialog, messagebox, ttk

from operation_log import log_operation, log_error

from file_generator import generate_file
from folder_cleaner import delete_empty_folders
from folder_scanner import find_empty_folders
from validator import validate_folder


def create_interface():
    root = tk.Tk()
    root.title("Утилита файловой системы")
    root.geometry("700x500")

    tabs = ttk.Notebook(root)
    tabs.pack(fill="both", expand=True)

    cleaner_tab = ttk.Frame(tabs, padding=10)
    generator_tab = ttk.Frame(tabs, padding=10)
    tabs.add(cleaner_tab, text="Очистка папок")
    tabs.add(generator_tab, text="Генератор файлов")

    # Первая вкладка: поиск и удаление пустых папок
    path_var = tk.StringVar()

    def choose_folder():
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)
            folder_list.delete(0, tk.END)
            exclusion_list.delete(0, tk.END)

    def scan_folders():
        path = path_var.get().strip()

        try:
            path = validate_folder(path)
        except ValueError as error:
            messagebox.showerror("Ошибка", str(error))
            return

        folder_list.delete(0, tk.END)

        try:
            found = find_empty_folders(path, exclusion_list.get(0, tk.END))
        except OSError as error:
            log_error(f"Ошибка сканирования {path}: {error}")
            messagebox.showerror("Ошибка сканирования", str(error))
            return

        for folder in found:
            if os.path.normcase(os.path.abspath(folder)) != os.path.normcase(os.path.abspath(path)):
                folder_list.insert(tk.END, folder)
        log_operation(f"Поиск пустых папок: {path}; найдено: {folder_list.size()}")
        if folder_list.size() == 0:
            messagebox.showinfo("Результат", "Пустые вложенные папки не найдены.")

    def delete_selected():
        indices = folder_list.curselection()

        if not indices:
            messagebox.showwarning("Удаление", "Сначала выберите папки в списке.")
            return

        selected = [folder_list.get(index) for index in indices]

        if not messagebox.askyesno(
                "Подтверждение удаления",
                f"Удалить выбранные папки ({len(selected)})?\n"
                "Они не попадут в корзину."
        ):
            return

        deleted, errors = delete_empty_folders(path_var.get().strip(), selected)
        log_operation(f"Удалено пустых папок: {len(deleted)}")
        for path, error in errors:
            log_error(f"Не удалось удалить {path}: {error}")

        for index in reversed(indices):
            if folder_list.get(index) in deleted:
                folder_list.delete(index)

        messagebox.showinfo("Результат", f"Удалено папок: {len(deleted)}")

        if errors:
            details = "\n".join(f"{path}: {error}" for path, error in errors)
            messagebox.showwarning("Не удалось удалить", details)

    def select_all_folders():
        folder_list.selection_set(0, tk.END)

    ttk.Label(cleaner_tab, text="Папка для проверки:").pack(anchor="w")
    ttk.Entry(cleaner_tab, textvariable=path_var).pack(fill="x", pady=5)
    ttk.Button(cleaner_tab, text="Выбрать папку", command=choose_folder).pack(anchor="w")
    ttk.Button(cleaner_tab, text="Найти пустые папки", command=scan_folders).pack(
        anchor="w", pady=10
    )

    def add_exclusion():
        if not os.path.isdir(path_var.get().strip()):
            messagebox.showerror("Ошибка", "Сначала выберите папку для проверки.")
            return

        folder = filedialog.askdirectory(initialdir=path_var.get().strip())
        if not folder:
            return

        if os.path.normcase(os.path.abspath(folder)) == os.path.normcase(
            os.path.abspath(path_var.get().strip())
        ):
            messagebox.showerror("Ошибка", "Нельзя исключить исходную папку.")
            return

        if folder not in exclusion_list.get(0, tk.END):
            exclusion_list.insert(tk.END, folder)
            folder_list.delete(0, tk.END)

    def remove_exclusion():
        for index in reversed(exclusion_list.curselection()):
            exclusion_list.delete(index)
        folder_list.delete(0, tk.END)

    ttk.Label(cleaner_tab, text="Исключённые папки:").pack(anchor="w")
    exclusion_list = tk.Listbox(cleaner_tab, height=2, exportselection=False)
    exclusion_list.pack(fill="x", pady=5)

    exclusion_buttons = ttk.Frame(cleaner_tab)
    exclusion_buttons.pack(fill="x")
    ttk.Button(
        exclusion_buttons, text="Добавить исключение", command=add_exclusion
    ).pack(side="left")
    ttk.Button(
        exclusion_buttons, text="Убрать исключение", command=remove_exclusion
    ).pack(side="left", padx=5)

    folder_list = tk.Listbox(cleaner_tab, selectmode=tk.EXTENDED, exportselection=False)
    folder_list.pack(fill="both", expand=True)
    ttk.Button(
        cleaner_tab, text="Выбрать всё", command=select_all_folders
    ).pack(anchor="w", pady=5)

    ttk.Button(
        cleaner_tab, text="Удалить выбранные", command=delete_selected
    ).pack(anchor="e", pady=10)

    # Вторая вкладка: создание тестовых файлов
    output_folder_var = tk.StringVar()
    file_name_var = tk.StringVar()
    file_size_var = tk.StringVar(value="1")
    unit_var = tk.StringVar(value="КБ")
    content_var = tk.StringVar(value="Нули")
    status_var = tk.StringVar(value="Ожидание")

    updates = queue.Queue()
    cancel_event = None
    running = False

    def choose_output_folder():
        folder = filedialog.askdirectory()
        if folder:
            output_folder_var.set(folder)

    def finish_operation():
        nonlocal running
        running = False
        create_button.config(state="normal")
        cancel_button.config(state="disabled")

    def check_updates():
        try:
            while True:
                kind, value = updates.get_nowait()

                if kind == "progress":
                    progress_bar["value"] = value
                    status_var.set(f"Создано: {value}%")
                elif kind == "done":
                    finish_operation()
                    status_var.set("Файл создан")
                    log_operation(f"Создан файл: {value}")
                    messagebox.showinfo("Готово", f"Файл создан:\n{value}")
                elif kind == "cancelled":
                    finish_operation()
                    status_var.set("Создание отменено")
                    log_operation("Создание файла отменено")
                elif kind == "error":
                    finish_operation()
                    status_var.set("Ошибка")
                    log_error(f"Ошибка создания файла: {value}")
                    messagebox.showerror("Ошибка создания файла", value)
        except queue.Empty:
            pass

        if running:
            root.after(50, check_updates)

    def cancel_creation():
        if cancel_event is not None:
            cancel_event.set()
            cancel_button.config(state="disabled")
            status_var.set("Отмена...")

    def create_file():
        nonlocal cancel_event, running

        if running:
            return

        folder = output_folder_var.get().strip()
        name = file_name_var.get().strip()
        unit = unit_var.get()
        content_type = content_var.get()
        target = os.path.join(folder, name)

        try:
            size = int(file_size_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Размер должен быть целым числом.")
            return

        overwrite = False
        if os.path.isfile(target):
            overwrite = messagebox.askyesno(
                "Файл уже существует",
                f"Файл {name} уже существует. Перезаписать его?"
            )
            if not overwrite:
                return

        cancel_event = threading.Event()
        running = True
        progress_bar["value"] = 0
        status_var.set("Создание файла...")
        create_button.config(state="disabled")
        cancel_button.config(state="normal")

        def worker():
            try:
                path = generate_file(
                    folder, name, size, unit, content_type,
                    overwrite=overwrite,
                    progress_callback=lambda done, total: updates.put(
                        ("progress", done * 100 // total)
                    ),
                    cancel_event=cancel_event
                )
            except InterruptedError:
                updates.put(("cancelled", None))
            except (ValueError, OSError) as error:
                updates.put(("error", str(error)))
            else:
                updates.put(("done", path))

        threading.Thread(target=worker).start()
        root.after(50, check_updates)

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

    create_button = ttk.Button(
        generator_tab, text="Создать файл", command=create_file
    )
    create_button.pack(anchor="e", pady=(15, 5))

    progress_bar = ttk.Progressbar(generator_tab, maximum=100)
    progress_bar.pack(fill="x", pady=5)

    ttk.Label(generator_tab, textvariable=status_var).pack(anchor="w")

    cancel_button = ttk.Button(
        generator_tab, text="Отмена", command=cancel_creation,
        state="disabled"
    )
    cancel_button.pack(anchor="e", pady=5)

    root.mainloop()
