#task2

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

# 从项目一中复用Task 和 TaskList 
class Task:
     def __init__(self, name: str, minutes: int):
        self.name = name
        self.minutes = minutes

#任务列表管理器
#包含添加、删除、更新、清空和获取任务的功能

class TaskList:
    def __init__(self):
        self._tasks = []

    def add(self, task: Task):
        self._tasks.append(task)

    def delete(self, index: int):
        if 0 <= index < len(self._tasks):
            del self._tasks[index]

    def update(self, index: int, new_task: Task):
        if 0 <= index < len(self._tasks):
            self._tasks[index] = new_task

    def clear(self):
        self._tasks.clear()

    def get_all(self) -> list[Task]:
        return self._tasks.copy() # 返回副本

# 添加任务对话框 

class AddTaskDialog(tk.Toplevel):
    def __init__(self, parent, on_ok):
        super().__init__(parent)
        self.title("添加新任务")
        self.on_ok = on_ok  # 将新任务传回主窗口
        self.transient(parent)
        self.grab_set()

        # 任务名称
        ttk.Label(self, text="任务名称:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(self, textvariable=self.name_var, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        name_entry.focus()

        # 时长
        ttk.Label(self, text="时长(分钟):").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.min_var = tk.IntVar(value=5)
        ttk.Spinbox(self, from_=1, to=180, textvariable=self.min_var, width=10).grid(row=1, column=1, padx=10, pady=10)

        # 按钮
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="确定", command=self._on_ok).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side="left", padx=5)

        # 居中显示
        self.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")

    def _on_ok(self):
        name = self.name_var.get().strip()
        minutes = self.min_var.get()

        if not name:
            messagebox.showerror("错误", "任务名称不能为空！", parent=self)
            return

        # 通过回调函数将任务对象传回主应用
        self.on_ok(Task(name, minutes))
        self.destroy()


# 主应用

class MainApp:
    def __init__(self, root_window: tk.Tk):
        self.root = root_window
        root_window.title("团队会议倒计时器 (项目二)")
        root_window.geometry("650x450")
        self.task_list = TaskList()

        # UI 
        # 顶部标题
        title_label = ttk.Label(root_window, text="团队会议任务管理器", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 按钮框架
        btn_frame = ttk.Frame(root_window)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="+ 添加任务", command=self._open_add_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ 删除选中", command=self._delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ 清空所有", command=self._clear_all).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📊 统计信息", command=self._show_stats).pack(side="left", padx=5)
        # 项目二中的新增内容：CSV导入/导出按钮
        ttk.Button(btn_frame, text="📥 导入CSV", command=self._import_csv).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📤 导出CSV", command=self._export_csv).pack(side="left", padx=5)

        # 统计信息
        self.stats_frame = ttk.LabelFrame(root_window, text="会议统计", padding=10)
        self.stats_frame.pack(fill="x", padx=20, pady=5)
        self.total_tasks_label = ttk.Label(self.stats_frame, text="总任务数: 0")
        self.total_tasks_label.pack(side="left", padx=20)
        self.total_time_label = ttk.Label(self.stats_frame, text="总时长: 0 分钟")
        self.total_time_label.pack(side="left", padx=20)

        # 任务列表
        tree_frame = ttk.Frame(root_window)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("#1", "#2", "#3")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        self.tree.heading("#1", text="序号")
        self.tree.heading("#2", text="任务名称")
        self.tree.heading("#3", text="时长(分钟)")
        self.tree.column("#1", width=60, anchor="center")
        self.tree.column("#2", width=350)
        self.tree.column("#3", width=100, anchor="center")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定双击事件编辑任务
        self.tree.bind("<Double-1>", self._edit_task)

    # 项目1原有的方法
   
    def _open_add_dialog(self):
        dialog = AddTaskDialog(self.root, on_ok=self._on_task_added)
        self.root.wait_window(dialog)
    def _on_task_added(self, task):
        self.task_list.add(task)
        self._refresh_treeview()
        self._update_stats()
    def _refresh_treeview(self):
        self.tree.delete(*self.tree.get_children())
        for i, task in enumerate(self.task_list.get_all(), 1):
            self.tree.insert("", "end", values=(i, task.name, task.minutes))
    def _update_stats(self):
        tasks = self.task_list.get_all()
        total_tasks = len(tasks)
        total_time = sum(task.minutes for task in tasks)
        self.total_tasks_label.config(text=f"总任务数: {total_tasks}")
        self.total_time_label.config(text=f"总时长: {total_time} 分钟")
    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected: return
        if messagebox.askyesno("确认", "确定删除选中任务?"):
            for item in reversed(selected):
                index = self.tree.index(item)
                self.task_list.delete(index)
            self._refresh_treeview()
            self._update_stats()
    def _clear_all(self):
        if messagebox.askyesno("确认", "确定清空所有任务?"):
            self.task_list.clear()
            self._refresh_treeview()
            self._update_stats()
    def _show_stats(self):
        tasks = self.task_list.get_all()
        if not tasks:
            messagebox.showinfo("统计", "无任务")
            return
        details = "\n".join([f"{i+1}. {t.name} ({t.minutes}分钟)" for i, t in enumerate(tasks)])
        messagebox.showinfo("统计", details)
    def _edit_task(self, event):
        selected = self.tree.selection()
        if not selected: return
        item = selected[0]
        index = self.tree.index(item)
        task = self.task_list.get_all()[index]
        self._open_edit_dialog(index, task)
    def _open_edit_dialog(self, index, task):
        # 这是一个简化版的编辑对话框，与AddTaskDialog类似
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑任务")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="任务名称:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        name_var = tk.StringVar(value=task.name)
        ttk.Entry(dialog, textvariable=name_var).grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(dialog, text="时长(分钟):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        min_var = tk.IntVar(value=task.minutes)
        ttk.Spinbox(dialog, from_=1, to=180, textvariable=min_var).grid(row=1, column=1, padx=10, pady=5)

        def on_save():
            new_task = Task(name_var.get().strip(), min_var.get())
            self.task_list.update(index, new_task)
            self._refresh_treeview()
            self._update_stats()
            dialog.destroy()

        ttk.Button(dialog, text="保存", command=on_save).grid(row=2, column=0, columnspan=2, pady=10)
        dialog.geometry(f"+{self.root.winfo_rootx() + 50}+{self.root.winfo_rooty() + 50}")

    #项目2：CSV导入/导出功能 

    # 导入CSV文件中的任务数据。
    #CSV格式：第一行为 '任务名称,时长(分钟)'
   #后续每行格式：'任务描述,整数'
       

    def _import_csv(self):
              
        file_path = filedialog.askopenfilename(
            title="选择要导入的CSV文件",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
            defaultextension=".csv"
        )

        if not file_path:
            return # 用户取消了选择

        try:
            with open(file_path, mode='r', encoding='utf-8-sig', newline='') as file:
                reader = csv.DictReader(file)

                # 验证CSV文件是否包含必要的列
                required_columns = ['任务名称', '时长(分钟)']
                if not all(col in reader.fieldnames for col in required_columns):
                    messagebox.showerror("格式错误", f"CSV文件缺少必要的列！\n需要: {', '.join(required_columns)}", parent=self.root)
                    return

                imported_tasks = []
                line_number = 2 # 从第二行开始计算（跳过表头）
                for row in reader:
                    task_name = row['任务名称'].strip()
                    duration_str = row['时长(分钟)'].strip()

                    # 数据验证
                    if not task_name:
                        messagebox.showwarning("数据警告", f"第 {line_number} 行：任务名称为空，已跳过。", parent=self.root)
                        line_number += 1
                        continue
                    try:
                        duration = int(duration_str)
                        if duration <= 0:
                            raise ValueError
                    except ValueError:
                        messagebox.showwarning("数据警告", f"第 {line_number} 行：时长 '{duration_str}' 不是有效的正整数，已跳过。", parent=self.root)
                        line_number += 1
                        continue

                    imported_tasks.append(Task(task_name, duration))
                    line_number += 1

                if not imported_tasks:
                    messagebox.showinfo("提示", "CSV文件中没有找到有效可导入的任务。", parent=self.root)
                    return

                # 询问用户是否清空现有任务
                if self.task_list.get_all():
                    if messagebox.askyesno("确认导入", f"即将导入 {len(imported_tasks)} 个任务。\n是否清空当前所有任务？", parent=self.root):
                        self.task_list.clear()
                
                # 添加导入的任务
                for task in imported_tasks:
                    self.task_list.add(task)
                
                self._refresh_treeview()
                self._update_stats()
                messagebox.showinfo("成功", f"成功导入 {len(imported_tasks)} 个任务！", parent=self.root)

        except FileNotFoundError:
            messagebox.showerror("错误", f"文件未找到: {file_path}", parent=self.root)
        except Exception as e:
            messagebox.showerror("导入失败", f"发生未知错误: {e}", parent=self.root)

#将当前所有任务导出到CSV文件
    def _export_csv(self):
    
        tasks = self.task_list.get_all()
        if not tasks:
            messagebox.showwarning("提示", "当前没有任务可以导出。", parent=self.root)
            return

        file_path = filedialog.asksaveasfilename(
            title="保存任务到CSV文件",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
            defaultextension=".csv",
            initialfile="会议任务导出.csv"
        )

        if not file_path:
            return # 用户取消了选择

        try:
            with open(file_path, mode='w', encoding='utf-8-sig', newline='') as file:
                fieldnames = ['任务名称', '时长(分钟)']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader() # 写入表头
                for task in tasks:
                    writer.writerow({'任务名称': task.name, '时长(分钟)': task.minutes})

            messagebox.showinfo("成功", f"任务已成功导出到:\n{file_path}", parent=self.root)

        except Exception as e:
            messagebox.showerror("导出失败", f"发生未知错误: {e}", parent=self.root)


# 程序入口

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
    
