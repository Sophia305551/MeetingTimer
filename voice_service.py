import pyttsx3
import threading
import logging
from typing import Optional


class VoiceService:
    def __init__(self):
        self.engine: Optional[pyttsx3.Engine] = None
        self._initialize_engine()

    def _initialize_engine(self):
        """初始化语音引擎"""
        try:
            self.engine = pyttsx3.init()
            # 设置语音属性
            voices = self.engine.getProperty('voices')
            if voices:
                # 尝试使用中文语音（如果可用）
                for voice in voices:
                    if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # 如果没有中文语音，使用第一个可用语音
                    self.engine.setProperty('voice', voices[0].id)

            # 设置语速和音量
            self.engine.setProperty('rate', 150)  # 语速
            self.engine.setProperty('volume', 0.8)  # 音量

            logging.info("语音服务初始化成功")

        except Exception as e:
            logging.error(f"语音服务初始化失败: {e}")
            self.engine = None

    def speak(self, text: str, async_mode: bool = True):
        """
        朗读文本

        Args:
            text: 要朗读的文本
            async_mode: 是否异步执行（不阻塞主线程）
        """
        if not self.engine:
            logging.warning("语音引擎未初始化，无法朗读")
            return

        def _speak():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logging.error(f"语音朗读失败: {e}")

        if async_mode:
            # 在新线程中执行，避免阻塞UI
            thread = threading.Thread(target=_speak, daemon=True)
            thread.start()
        else:
            _speak()

    def announce_task_completion(self, task_name: str, next_task_name: str = None):
        """播报任务完成通知"""
        if next_task_name:
            message = f"任务 {task_name} 已完成。接下来进行：{next_task_name}"
        else:
            message = f"任务 {task_name} 已完成。会议结束！"

        self.speak(message)
        logging.info(f"语音提醒: {message}")

    def announce_meeting_start(self, total_tasks: int, total_minutes: int):
        """播报会议开始"""
        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours > 0:
            time_str = f"{hours}小时{minutes}分钟"
        else:
            time_str = f"{minutes}分钟"

        message = f"会议开始！本次会议共有{total_tasks}个任务，总时长{time_str}。"
        self.speak(message)
        logging.info(f"会议开始提醒: {message}")

    def announce_break_time(self, break_minutes: int):
        """播报休息时间"""
        message = f"休息时间到，请休息{break_minutes}分钟。"
        self.speak(message)

    def test_voice(self):
        """测试语音功能"""
        if self.engine:
            self.speak("语音提醒功能测试成功！")
            return True
        else:
            logging.error("语音引擎未就绪")
            return False

    def __del__(self):
        """清理资源"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass