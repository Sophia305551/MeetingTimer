import tkinter as tk
from tkinter import ttk, messagebox
from task_list import TaskList
from add_task_dialog import AddTaskDialog
from task import Task


class MainApp:
    def __init__(self, root_window: tk.Tk):  # 重命名参数避免隐藏
        self.root = root_window  # 使用不同的变量名
        root_window.title("团队会议倒计时器")
        root_window.geometry("500x400")
        self.task_list = TaskList()

        # 顶部标题
        title_label = ttk.Label(root_window, text="团队会议任务管理器", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 按钮框架
        btn_frame = ttk.Frame(root_window)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="+ 添加任务", command=self._open_add_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ 删除选中", command=self._delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ 清空所有", command=self._clear_all).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📊 统计信息", command=self._show_stats).pack(side="left", padx=5)

        # 统计信息显示
        self.stats_frame = ttk.LabelFrame(root_window, text="会议统计", padding=10)
        self.stats_frame.pack(fill="x", padx=20, pady=5)

        self.total_tasks_label = ttk.Label(self.stats_frame, text="总任务数: 0")
        self.total_tasks_label.pack(side="left", padx=20)

        self.total_time_label = ttk.Label(self.stats_frame, text="总时长: 0 分钟")
        self.total_time_label.pack(side="left", padx=20)

        # Treeview
        tree_frame = ttk.Frame(root_window)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("#1", "#2", "#3")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)

        # 设置列
        self.tree.heading("#1", text="序号")
        self.tree.heading("#2", text="任务名称")
        self.tree.heading("#3", text="时长(分钟)")

        self.tree.column("#1", width=60, anchor="center")
        self.tree.column("#2", width=250)
        self.tree.column("#3", width=100, anchor="center")

        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定双击事件编辑任务
        self.tree.bind("<Double-1>", self._edit_task)

    def _open_add_dialog(self):
        dialog = AddTaskDialog(self.root, on_ok=self._on_task_added)
        self.root.wait_window(dialog)

    def _on_task_added(self, task):
        self.task_list.add(task)
        self._refresh_treeview()
        self._update_stats()

    def _refresh_treeview(self):
        """刷新Treeview显示"""
        self.tree.delete(*self.tree.get_children())
        tasks = self.task_list.get_all()

        for i, task in enumerate(tasks, 1):
            self.tree.insert("", "end", values=(i, task.name, task.minutes))

    def _update_stats(self):
        """更新统计信息"""
        total_tasks = len(self.task_list.get_all())
        total_time = sum(task.minutes for task in self.task_list.get_all())

        self.total_tasks_label.config(text=f"总任务数: {total_tasks}")
        self.total_time_label.config(text=f"总时长: {total_time} 分钟")

    def _delete_selected(self):
        """删除选中的任务"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的任务！")
            return

        if messagebox.askyesno("确认删除", "确定要删除选中的任务吗？"):
            # 获取选中的索引并删除（从后往前删除避免索引变化）
            for item in reversed(selected):
                index = self.tree.index(item)
                self.task_list.delete(index)

            self._refresh_treeview()
            self._update_stats()

    def _clear_all(self):
        """清空所有任务"""
        if not self.task_list.get_all():
            messagebox.showinfo("提示", "任务列表已经是空的！")
            return

        if messagebox.askyesno("确认清空", "确定要清空所有任务吗？此操作不可撤销！"):
            self.task_list.clear()
            self._refresh_treeview()
            self._update_stats()

    def _show_stats(self):
        """显示详细统计信息"""
        tasks = self.task_list.get_all()
        total_tasks = len(tasks)
        total_time = sum(task.minutes for task in tasks)

        if total_tasks == 0:
            messagebox.showinfo("统计信息", "当前没有任务")
            return

        # 构建任务列表
        task_details = "\n".join([f"{i + 1}. {task.name} ({task.minutes}分钟)"
                                  for i, task in enumerate(tasks)])

        avg_time = total_time / total_tasks if total_tasks > 0 else 0

        messagebox.showinfo("详细统计",
                            f"总任务数: {total_tasks}\n"
                            f"总时长: {total_time} 分钟\n"
                            f"平均时长: {avg_time:.1f} 分钟\n"
                            f"预计会议时间: {total_time // 60}小时{total_time % 60}分钟\n\n"
                            f"任务列表:\n{task_details}")

    def _edit_task(self, event=None):  # 添加默认值 None，表示参数是可选的
        """双击编辑任务"""
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            index = self.tree.index(item)
            tasks = self.task_list.get_all()
            if 0 <= index < len(tasks):
                task = tasks[index]
                self._open_edit_dialog(index, task)

    def _open_edit_dialog(self, index, task):
        """打开编辑对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑任务")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100,
                                    self.root.winfo_rooty() + 100))

        ttk.Label(dialog, text="任务名称:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        name_var = tk.StringVar(value=task.name)
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=25)
        name_entry.grid(row=0, column=1, padx=10)
        name_entry.focus()
        name_entry.select_range(0, tk.END)

        ttk.Label(dialog, text="时长(分钟):").grid(row=1, column=0, padx=10, sticky="e")
        min_var = tk.IntVar(value=task.minutes)
        ttk.Spinbox(dialog, from_=1, to=180, textvariable=min_var, width=10).grid(row=1, column=1, padx=10)

        def save_changes():
            new_name = name_var.get().strip()
            if not new_name:
                messagebox.showwarning("警告", "任务名称不能为空！")
                return

            # 更新任务
            updated_task = Task(name=new_name, minutes=min_var.get())
            self.task_list.update(index, updated_task)
            self._refresh_treeview()
            self._update_stats()
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="保存", command=save_changes).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side="left")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)  # 这里传递的是 root 变量
    root.mainloop()