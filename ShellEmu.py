import os
import tkinter as tk
from tkinter import scrolledtext
import argparse

# глобальная конфигурация
config = {}

def run_command(event=None):
    global out, inpe
    command_line = inpe.get()
    inpe.delete(0, tk.END)

    # показать, что мы ввели
    out.config(state=tk.NORMAL)
    out.insert(tk.END, f"> {command_line}\n")

    if not command_line.strip():
        out.config(state=tk.DISABLED)
        return

    # раскрытие переменных окружения ($HOME и т.д.)
    command_line = os.path.expandvars(command_line)
    parts = command_line.split()
    cmd = parts[0]
    args = parts[1:]

    # команды-заглушки
    if cmd == "exit":
        out.insert(tk.END, "Выход...\n")
        root.quit()

    elif cmd == "ls":
        out.insert(tk.END, f"Вызвана команда: ls, аргументы: {args}\n")

    elif cmd == "cd":
        out.insert(tk.END, f"Вызвана команда: cd, аргументы: {args}\n")

    else:
        out.insert(tk.END, f"Ошибка: неизвестная команда '{cmd}'\n")

    out.config(state=tk.DISABLED)
    out.see(tk.END)

def get_config():
    parser = argparse.ArgumentParser(description="Эмулятор оболочки")
    parser.add_argument("--vfs", default="default.json", help="Файл виртуальной ФС")
    parser.add_argument("--debug", action="store_true", help="Включить отладку")
    parser.add_argument("--name", default="myvfs", help="Имя виртуальной ФС (отображается в приглашении)")

    args = parser.parse_args()

    # Преобразуем в словарь
    config = {
        "vfs": args.vfs,
        "debug": args.debug,
        "name": args.name
    }
    return config

config = get_config()

# отладочный вывод
print("Параметры эмулятора:")
for key, value in config.items():
    print(f"{key} = {value}")
#GUI
root = tk.Tk()
root.title("VFS Emulator")
root.geometry("800x500")

main = tk.Frame(root)
main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# строка с prompt
prompt = tk.Label(main, text="user@host $ ", font=("Courier", 10))
prompt.pack(side=tk.LEFT)

# поле ввода
inpe = tk.Entry(main, font=("Courier", 10))
inpe.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
inpe.bind("<Return>", run_command)

# кнопка Enter
ent = tk.Button(main, text="Enter", command=run_command)
ent.pack(side=tk.RIGHT)

# окно вывода
out = scrolledtext.ScrolledText(root, height=20, width=80)
out.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
out.config(state=tk.DISABLED)

inpe.focus()
root.mainloop()
