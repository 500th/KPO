import tkinter as tk
from tkinter import ttk


root = tk.Tk()
root.title("Утилита файловой системы")
root.geometry("700x450")

tabs = ttk.Notebook(root)
tabs.pack(fill="both", expand=True)

cleaner_tab = ttk.Frame(tabs)
generator_tab = ttk.Frame(tabs)

tabs.add(cleaner_tab, text="Очистка папок")
tabs.add(generator_tab, text="Генератор файлов")

root.mainloop()