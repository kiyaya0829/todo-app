import json
import os
import tkinter as tk
from tkinter import messagebox
import datetime
import sys

# =========================
# 文件名
# =========================
FILE_NAME = "tasks.json"

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# =========================
# 读取任务
# =========================
def load_tasks():

    # 如果文件不存在
    if not os.path.exists(FILE_NAME):
        return []

    with open(FILE_NAME, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# 保存任务
# =========================
def save_tasks(tasks):

    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)


# =========================
# 添加任务
# =========================
def add_task(tasks, title, priority):

    new_task = {
        "title": title,
        "done": False,
        "priority": priority,
        "created": datetime.datetime.now().strftime("%m-%d")
    }

    tasks.append(new_task)
    save_tasks(tasks)

# =========================
# 删除任务
# =========================
def delete_task(tasks, index):

    if 0 <= index < len(tasks):

        tasks.pop(index)

        save_tasks(tasks)

# =========================
# 完成任务
# =========================
def toggle_task(tasks, index):

    if 0 <= index < len(tasks):

        tasks[index]["done"] = not tasks[index]["done"]

        save_tasks(tasks)


# =========================
# GUI
# =========================

# 读取任务
tasks = load_tasks()

visible_index_map = []

# 当前优先级
current_priority = "medium"

# 创建窗口
root = tk.Tk()

icon = tk.PhotoImage(file=resource_path("icon.png"))
root.iconphoto(True, icon)

# 标题
root.title("Todo App")

# 窗口大小
root.geometry("500x450")

# =========================
# 提示文字
# =========================
title_label = tk.Label(root, text="请输入事件：")

title_label.pack(pady=5)

priority_label = tk.Label(root, text="当前优先级：🟡 不急不急")

priority_label.pack(pady=5)

def update_priority_label():
    if current_priority == "high":
        priority_label.config(text="当前优先级：🔴 急急急")
    elif current_priority == "medium":
        priority_label.config(text="当前优先级：🟡 不急不急")
    else:
        priority_label.config(text="当前优先级：🟢 想起来再说")

# =========================
# 输入框
# =========================
task_entry = tk.Entry(root, width=30)
task_entry.pack(pady=10)
def enter_add(event):
    gui_add_task(current_priority)
    return "break"
task_entry.bind("<Return>", enter_add)

# =========================
# 添加任务函数
# =========================
def gui_add_task(priority=None):

    global current_priority

    # 如果传入了优先级
    if priority is not None:
        current_priority = priority

    # 获取输入框内容
    title = task_entry.get()

    # 防止空内容
    if title == "":
        return

    # 调用逻辑函数
    add_task(tasks, title, current_priority)

    # 刷新界面
    refresh_listbox()

    # 清空输入框
    task_entry.delete(0, tk.END)

# =========================
# 优先级按钮区域
# =========================
priority_frame = tk.Frame(root)

priority_frame.pack(pady=10)

def set_priority(p):
    global current_priority
    current_priority = p
    update_priority_label()

# =========================
# HIGH 按钮
# =========================
high_button = tk.Button(
    priority_frame,
    text="急急急",
    width=15,
    command=lambda: set_priority("high")
)
high_button.pack(side=tk.LEFT, padx=5)

# =========================
# MEDIUM 按钮
# =========================
medium_button = tk.Button(
    priority_frame,
    text="不急不急",
    width=15,
    command=lambda: set_priority("medium")
)

medium_button.pack(side=tk.LEFT, padx=5)

# =========================
# LOW 按钮
# =========================
low_button = tk.Button(
    priority_frame,
    text="想起来再说",
    width=15,
    command=lambda: set_priority("low")
)

low_button.pack(side=tk.LEFT, padx=5)

def gui_toggle_task():

    selected = task_listbox.curselection()

    if not selected:
        return

    index = selected[0]

    toggle_task(tasks, index)

    refresh_listbox()


# =========================
# GUI 删除任务
# =========================
def gui_delete_task():

    selected = task_listbox.curselection()

    if not selected:
        return

    list_index = selected[0]

    real_index = visible_index_map[list_index]

    if real_index is None:
        return

    confirm = messagebox.askyesno(
        "确认删除",
        "确定删除这个任务吗？"
    )

    if confirm:
        delete_task(tasks, real_index)
        refresh_listbox()

# =========================
# 双击完成任务
# =========================
def on_double_click(event):

    selected = task_listbox.curselection()
    if not selected:
        return

    list_index = selected[0]

    real_index = visible_index_map[list_index]

    if real_index is None:
        return  # 点击的是标题

    toggle_task(tasks, real_index)

    refresh_listbox()

# =========================
# 操作按钮区域
# =========================
action_frame = tk.Frame(root)

action_frame.pack(pady=10)


# =========================
# 删除任务按钮
# =========================
delete_button = tk.Button(
    action_frame,
    text="删除任务",
    width=15,
    command=gui_delete_task
)

delete_button.pack(side=tk.LEFT, padx=10)


# =========================
# 任务列表
# =========================
task_listbox = tk.Listbox(
    root,
    width=50,
    height=15,
    font=("Segoe UI Emoji", 12)
)

task_listbox.pack(pady=20)

task_listbox.bind("<Double-Button-1>", on_double_click)

# =========================
# 刷新任务列表
# =========================
def refresh_listbox():

    global visible_index_map
    visible_index_map = []

    task_listbox.delete(0, tk.END)

    high_tasks = []
    medium_tasks = []
    low_tasks = []

    for i, task in enumerate(tasks):

        if task["priority"] == "high":
            high_tasks.append((i, task))
        elif task["priority"] == "medium":
            medium_tasks.append((i, task))
        else:
            low_tasks.append((i, task))

    def add_group(title):
        task_listbox.insert(tk.END, title)
        visible_index_map.append(None)

    def add_item(i, task):
        status = "⬜" if not task["done"] else "☑"
        date = task.get("created", "")
        text = f"{status} {task['title']} ({date})"

        task_listbox.insert(tk.END, text)
        visible_index_map.append(i)

    # 高
    add_group("🔴 ===== 急 =====")
    for i, task in high_tasks:
        add_item(i, task)

    # 中
    add_group("")
    add_group("🟡 ===== 中 =====")
    for i, task in medium_tasks:
        add_item(i, task)

    # 低
    add_group("")
    add_group("🟢 ===== 低 =====")
    for i, task in low_tasks:
        add_item(i, task)

    update_priority_label()
refresh_listbox()

# 启动 GUI
root.mainloop()