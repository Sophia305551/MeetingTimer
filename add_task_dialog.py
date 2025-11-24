import tkinter as tk
from tkinter import ttk, messagebox
from task import Task


class AddTaskDialog(tk.Toplevel):
    def __init__(self, parent, on_ok):
        super().__init__(parent)
        self.title("添加子任务")
        self.resizable(False, False)
        self.on_ok = on_ok

        # 设置对话框属性
        self.transient(parent)  # 与父窗口关联
        self.grab_set()  # 模态对话框

        # 居中显示
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                  parent.winfo_rooty() + 50))

        # 创建变量
        self.name_var = tk.StringVar()
        self.min_var = tk.IntVar(value=15)

        # 创建界面
        ttk.Label(self, text="任务名称:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry = ttk.Entry(self, textvariable=self.name_var, width=25)
        self.entry.grid(row=0, column=1, padx=10)
        self.entry.focus()  # 让输入框默认获得焦点

        ttk.Label(self, text="时长(分钟):").grid(row=1, column=0, padx=10, sticky="e")
        ttk.Spinbox(self, from_=1, to=180, textvariable=self.min_var, width=10).grid(row=1, column=1, padx=10)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="确定", command=self._ok).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side="left")

        # 绑定回车键到确定按钮
        self.bind('<Return>', lambda e: self._ok())

    def _ok(self):
        name = self.name_var.get().strip()
        print(f"调试信息: 输入的任务名='{name}', 长度={len(name)}")

        if not name:
            messagebox.showwarning("警告", "任务名称不能为空！")
            self.entry.focus()  # 重新聚焦到输入框
            return

        # 验证时长是否有效
        try:
            minutes = self.min_var.get()
            if minutes <= 0:
                messagebox.showwarning("警告", "时长必须大于0分钟！")
                return
        except tk.TclError:
            messagebox.showwarning("警告", "请输入有效的时长！")
            return

        task = Task(name=name, minutes=minutes)
        self.on_ok(task)
        self.destroy()