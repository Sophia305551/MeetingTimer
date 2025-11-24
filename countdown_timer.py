import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime, timedelta
from task_list import TaskList
from voice_service import VoiceService


class CountdownTimer:
    def __init__(self, task_list: TaskList, voice_service: VoiceService):
        self.task_list = task_list
        self.voice_service = voice_service
        self.current_task_index = 0
        self.is_running = False
        self.is_paused = False
        self.remaining_time = 0
        self.total_elapsed_time = 0

    def start_meeting(self, on_timer_update, on_task_complete, on_meeting_end):
        """开始会议倒计时"""
        tasks = self.task_list.get_all()
        if not tasks:
            messagebox.showwarning("警告", "没有任务可以开始计时！")
            return False

        self.current_task_index = 0
        self.is_running = True
        self.is_paused = False
        self.total_elapsed_time = 0

        # 播报会议开始
        total_minutes = self.task_list.get_total_time()
        self.voice_service.announce_meeting_start(len(tasks), total_minutes)

        # 开始第一个任务
        self._start_current_task(on_timer_update, on_task_complete, on_meeting_end)
        return True

    def _start_current_task(self, on_timer_update, on_task_complete, on_meeting_end):
        """开始当前任务的倒计时"""
        if not self.is_running:
            return

        tasks = self.task_list.get_all()
        if self.current_task_index >= len(tasks):
            self._end_meeting(on_meeting_end)
            return

        current_task = tasks[self.current_task_index]
        self.remaining_time = current_task.minutes * 60  # 转换为秒

        # 在新线程中运行倒计时
        thread = threading.Thread(
            target=self._run_countdown,
            args=(current_task, on_timer_update, on_task_complete, on_meeting_end),
            daemon=True
        )
        thread.start()

    def _run_countdown(self, task, on_timer_update, on_task_complete, on_meeting_end):
        """运行倒计时"""
        start_time = time.time()

        while self.remaining_time > 0 and self.is_running:
            if not self.is_paused:
                # 更新UI
                if on_timer_update:
                    minutes = self.remaining_time // 60
                    seconds = self.remaining_time % 60
                    on_timer_update(task.name, minutes, seconds, self.current_task_index + 1)

                time.sleep(1)
                self.remaining_time -= 1
                self.total_elapsed_time += 1
            else:
                time.sleep(0.1)  # 暂停时降低CPU占用

        if self.is_running and self.remaining_time <= 0:
            # 任务完成
            tasks = self.task_list.get_all()
            next_task = None
            if self.current_task_index + 1 < len(tasks):
                next_task = tasks[self.current_task_index + 1].name

            # 播报任务完成
            self.voice_service.announce_task_completion(task.name, next_task)

            if on_task_complete:
                on_task_complete(task.name)

            # 移动到下一个任务
            self.current_task_index += 1
            self._start_current_task(on_timer_update, on_task_complete, on_meeting_end)

    def pause_timer(self):
        """暂停计时器"""
        self.is_paused = True

    def resume_timer(self):
        """恢复计时器"""
        self.is_paused = False

    def stop_timer(self):
        """停止计时器"""
        self.is_running = False
        self.is_paused = False

    def add_time_to_current_task(self, minutes: int):
        """为当前任务增加时间"""
        if self.is_running and not self.is_paused:
            self.remaining_time += minutes * 60
            return True
        return False

    def skip_current_task(self):
        """跳过当前任务"""
        if self.is_running:
            self.current_task_index += 1
            self.is_paused = False
            return True
        return False

    def _end_meeting(self, on_meeting_end):
        """结束会议"""
        self.is_running = False
        if on_meeting_end:
            on_meeting_end(self.total_elapsed_time)

        # 播报会议结束
        self.voice_service.speak("会议已结束，辛苦了！")