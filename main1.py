import tkinter as tk
from tkinter import ttk, messagebox
from task_list import TaskList
from add_task_dialog import AddTaskDialog
from task import Task
from countdown_timer import CountdownTimer
from voice_service import VoiceService


class MainApp:
    def __init__(self, root_window: tk.Tk):
        self.root = root_window
        root_window.title("团队会议倒计时器 - 带语音提醒")
        root_window.geometry("600x500")

        # 初始化服务
        self.task_list = TaskList()
        self.voice_service = VoiceService()
        self.countdown_timer = CountdownTimer(self.task_list, self.voice_service)

        self._create_ui()

        # 测试语音功能
        self._test_voice_on_startup()

    def _create_ui(self):
        """创建用户界面"""
        # 顶部标题
        title_label = ttk.Label(self.root, text="团队会议倒计时器 - 带语音提醒",
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 任务管理区域
        self._create_task_management_section()

        # 倒计时显示区域
        self._create_countdown_section()

        # 控制按钮区域
        self._create_control_buttons()

    def _create_task_management_section(self):
        """创建任务管理区域"""
        # 任务管理框架
        task_frame = ttk.LabelFrame(self.root, text="任务管理", padding=10)
        task_frame.pack(fill="x", padx=20, pady=5)

        # 按钮框架
        btn_frame = ttk.Frame(task_frame)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="+ 添加任务", command=self._open_add_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ 删除选中", command=self._delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ 清空所有", command=self._clear_all).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📊 统计信息", command=self._show_stats).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔊 测试语音", command=self._test_voice).pack(side="left", padx=5)

        # 统计信息显示
        self.stats_frame = ttk.Frame(task_frame)
        self.stats_frame.pack(fill="x", pady=5)

        self.total_tasks_label = ttk.Label(self.stats_frame, text="总任务数: 0")
        self.total_tasks_label.pack(side="left", padx=20)

        self.total_time_label = ttk.Label(self.stats_frame, text="总时长: 0 分钟")
        self.total_time_label.pack(side="left", padx=20)

        # Treeview
        tree_frame = ttk.Frame(task_frame)
        tree_frame.pack(fill="both", expand=True, pady=5)

        columns = ("#1", "#2", "#3")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

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

        self.tree.bind("<Double-1>", self._edit_task)

    def _create_countdown_section(self):
        """创建倒计时显示区域"""
        countdown_frame = ttk.LabelFrame(self.root, text="倒计时", padding=15)
        countdown_frame.pack(fill="x", padx=20, pady=10)

        # 当前任务显示
        self.current_task_label = ttk.Label(
            countdown_frame,
            text="当前任务: 未开始",
            font=("Arial", 12, "bold"),
            foreground="blue"
        )
        self.current_task_label.pack(pady=5)

        # 倒计时显示
        self.time_label = ttk.Label(
            countdown_frame,
            text="00:00",
            font=("Arial", 24, "bold"),
            foreground="red"
        )
        self.time_label.pack(pady=10)

        # 进度信息
        self.progress_label = ttk.Label(
            countdown_frame,
            text="任务进度: 0/0",
            font=("Arial", 10)
        )
        self.progress_label.pack(pady=5)

    def _create_control_buttons(self):
        """创建控制按钮区域"""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)

        self.start_btn = ttk.Button(control_frame, text="▶️ 开始会议",
                                    command=self._start_meeting)
        self.start_btn.pack(side="left", padx=5)

        self.pause_btn = ttk.Button(control_frame, text="⏸️ 暂停",
                                    command=self._pause_timer, state="disabled")
        self.pause_btn.pack(side="left", padx=5)

        self.resume_btn = ttk.Button(control_frame, text="▶️ 继续",
                                     command=self._resume_timer, state="disabled")
        self.resume_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(control_frame, text="⏹️ 停止",
                                   command=self._stop_timer, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        ttk.Button(control_frame, text="⏩ 跳过当前",
                   command=self._skip_current_task).pack(side="left", padx=5)

        ttk.Button(control_frame, text="➕ 加时5分钟",
                   command=lambda: self._add_time(5)).pack(side="left", padx=5)

    def _test_voice_on_startup(self):
        """启动时测试语音功能"""
        # 延迟测试，避免干扰启动
        self.root.after(1000, self._test_voice_quietly)

    def _test_voice_quietly(self):
        """静默测试语音功能"""
        if not self.voice_service.test_voice():
            messagebox.showwarning("语音提醒",
                                   "语音功能初始化失败。请检查：\n"
                                   "1. 系统是否安装语音合成引擎\n"
                                   "2. 音量是否开启\n"
                                   "3. 程序是否有音频访问权限")

    def _test_voice(self):
        """测试语音功能"""
        self.voice_service.speak("这是一次语音功能测试！如果听到此提示，说明语音提醒功能工作正常。")

    def _open_add_dialog(self):
        """打开添加任务对话框"""
        dialog = AddTaskDialog(self.root, on_ok=self._on_task_added)
        self.root.wait_window(dialog)

    def _on_task_added(self, task):
        """任务添加回调"""
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

    def _edit_task(self, event=None):
        """双击编辑任务"""
        # 修复：使用 _ 前缀表示未使用的参数
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

    def _start_meeting(self):
        """开始会议"""
        if not self.task_list.get_all():
            messagebox.showwarning("警告", "请先添加任务再开始会议！")
            return

        success = self.countdown_timer.start_meeting(
            on_timer_update=self._on_timer_update,
            on_task_complete=self._on_task_complete,
            on_meeting_end=self._on_meeting_end
        )

        if success:
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self.stop_btn.config(state="normal")

    def _on_timer_update(self, task_name, minutes, seconds, current_task_num):
        """定时器更新回调"""

        def update_ui():
            self.current_task_label.config(text=f"当前任务: {task_name}")
            self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")

            total_tasks = len(self.task_list.get_all())
            self.progress_label.config(text=f"任务进度: {current_task_num}/{total_tasks}")

            # 最后1分钟变为红色警告
            if minutes == 0 and seconds <= 30:
                self.time_label.config(foreground="red")
            elif minutes < 2:
                self.time_label.config(foreground="orange")
            else:
                self.time_label.config(foreground="green")

        # 修复：移除多余的参数
        self.root.after(0, update_ui)

    def _on_task_complete(self, task_name):
        """任务完成回调"""

        def update_ui():
            messagebox.showinfo("任务完成", f"任务 '{task_name}' 已完成！")

        # 修复：移除多余的参数
        self.root.after(0, update_ui)

    def _on_meeting_end(self, total_seconds):
        """会议结束回调"""

        def update_ui():
            total_minutes = total_seconds // 60
            self.current_task_label.config(text="会议结束！")
            self.time_label.config(text="00:00", foreground="blue")
            self.progress_label.config(text="所有任务已完成")

            messagebox.showinfo("会议结束",
                                f"会议已完成！\n总用时: {total_minutes}分钟")

            # 重置按钮状态
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            self.resume_btn.config(state="disabled")
            self.stop_btn.config(state="disabled")

        # 修复：移除多余的参数
        self.root.after(0, update_ui)

    def _pause_timer(self):
        """暂停计时器"""
        self.countdown_timer.pause_timer()
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="normal")

    def _resume_timer(self):
        """恢复计时器"""
        self.countdown_timer.resume_timer()
        self.resume_btn.config(state="disabled")
        self.pause_btn.config(state="normal")

    def _stop_timer(self):
        """停止计时器"""
        self.countdown_timer.stop_timer()
        self._reset_timer_ui()

    def _skip_current_task(self):
        """跳过当前任务"""
        if self.countdown_timer.skip_current_task():
            messagebox.showinfo("跳过任务", "已跳过当前任务")

    def _add_time(self, minutes):
        """为当前任务增加时间"""
        if self.countdown_timer.add_time_to_current_task(minutes):
            messagebox.showinfo("加时", f"已为当前任务增加{minutes}分钟")
        else:
            messagebox.showwarning("加时失败", "当前没有运行中的任务")

    def _reset_timer_ui(self):
        """重置计时器UI"""
        self.current_task_label.config(text="当前任务: 未开始")
        self.time_label.config(text="00:00", foreground="red")
        self.progress_label.config(text="任务进度: 0/0")

        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.resume_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()