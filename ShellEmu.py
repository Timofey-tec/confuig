import os
import tkinter as tk
from tkinter import scrolledtext
import argparse
import base64
import json

# глобальная конфигурация
config = {}
# текущий путь в VFS
current_path = ["/"]

# функция получения конфигурации из аргументов командной строки
def get_config():
    parser = argparse.ArgumentParser(description="Эмулятор оболочки")
    parser.add_argument("--vfs", default="VFS.json", help="Файл виртуальной ФС")
    parser.add_argument("--script", default=None, help="Путь к стартовому скрипту")
    parser.add_argument("--debug", action="store_true", help="Включить отладку")
    parser.add_argument("--name", default="VFS", help="Имя виртуальной ФС (отображается в приглашении)")

    args = parser.parse_args()

    return {
        "vfs": args.vfs,
        "script": args.script,
        "debug": args.debug,
        "name": args.name
    }

# получаем конфиг
config = get_config()
print("Параметры эмулятора:")
for key, value in config.items():
    print(f"{key} = {value}")

# загрузка VFS из файла
def load_vfs(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки VFS: {e}")
        return None

vfs_root = load_vfs(config.get("vfs", "VFS.json"))

def get_node_by_path(root, path_list):
    node = root
    for part in path_list[1:]:
        if node["type"] != "dir":
            return None
        found = None
        for child in node.get("children", []):
            if child["name"] == part:
                found = child
                break
        if not found:
            return None
        node = found
    return node


def resolve_path(current, target):
    parts = []
    if target.startswith("/"):
        parts = ["/"] + [p for p in target.split("/") if p and p != "/"]
    else:
        parts = current.copy()
        for p in target.split("/"):
            if p in ("", "."):
                continue
            elif p == "..":
                if len(parts) > 1:
                    parts.pop()
            else:
                parts.append(p)
    return parts


def cmd_ls(args):
    node = get_node_by_path(vfs_root, current_path)
    if not node or node["type"] != "dir":
        return "Ошибка: не каталог"
    result = []
    for child in node.get("children", []):
        if child["type"] == "dir":
            result.append(child["name"] + "/")
        else:
            result.append(child["name"])
    return "\n".join(result) if result else "(пусто)"


def cmd_cd(args):
    global current_path
    if not args:
        current_path = ["/"]
        return "Перешли в корень"
    new_path = resolve_path(current_path, args[0])
    node = get_node_by_path(vfs_root, new_path)
    if not node or node["type"] != "dir":
        return f"Ошибка: путь {'/'.join(new_path)} не найден"
    current_path = new_path
    prompt.config(text=f"user@{config['name']}:{'/'.join(current_path) if len(current_path) > 1 else '/'} $ ")
    return "Текущий путь: " + "/".join(current_path[1:]) if len(current_path) > 1 else "/"


def cmd_cat(args):
    if not args:
        return "Ошибка: нужно указать имя файла"
    target_path = resolve_path(current_path, args[0])
    node = get_node_by_path(vfs_root, target_path)
    if not node or node["type"] != "file":
        return f"Ошибка: файл {'/'.join(target_path)} не найден"
    content = node.get("content", "")
    try:
        decoded = base64.b64decode(content).decode("utf-8")
        return decoded
    except Exception:
        return content

# функция выполнения команд
def run_command(command_line=None):
    global out, inpe
    if command_line is None:
        command_line = inpe.get()
        inpe.delete(0, tk.END)

    out.config(state=tk.NORMAL)
    out.insert(tk.END, f"> {command_line}\n")

    if not command_line.strip():
        out.config(state=tk.DISABLED)
        return

    command_line = os.path.expandvars(command_line)
    parts = command_line.split()
    cmd = parts[0]
    args = parts[1:]

    if cmd == "exit":
        out.insert(tk.END, "Выход...\n")
        root.quit()

    elif cmd == "ls":
        out.insert(tk.END, cmd_ls(args) + "\n")

    elif cmd == "cd":
        out.insert(tk.END, cmd_cd(args) + "\n")

    elif cmd == "cat":
        out.insert(tk.END, cmd_cat(args) + "\n")

    elif cmd == "conf-dump":
        out.insert(tk.END, "Текущая конфигурация:\n")
        for key, value in config.items():
            out.insert(tk.END, f"{key} = {value}\n")

    else:
        out.insert(tk.END, f"Ошибка: неизвестная команда '{cmd}'\n")

    out.config(state=tk.DISABLED)
    out.see(tk.END)



# GUI
root = tk.Tk()
root.title("VFS Emulator")
root.geometry("800x500")

main = tk.Frame(root)
main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

prompt = tk.Label(main, text="user@host $ ", font=("Courier", 10))
prompt.pack(side=tk.LEFT)

inpe = tk.Entry(main, font=("Courier", 10))
inpe.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
inpe.bind("<Return>", lambda event: run_command())

ent = tk.Button(main, text="Enter", command=lambda: run_command())
ent.pack(side=tk.RIGHT)

out = scrolledtext.ScrolledText(root, height=20, width=80)
out.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
out.config(state=tk.DISABLED)

# функция выполнения стартового скрипта
def run_startup_script(script_path):
    if not script_path or not os.path.isfile(script_path):
        return
    with open(script_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            run_command(line)

# выполнить стартовый скрипт, если указан
run_startup_script(config.get("script"))

inpe.focus()
root.mainloop()
