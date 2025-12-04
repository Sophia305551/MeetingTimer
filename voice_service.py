# 模拟VoiceService类，避免pyttsx3依赖报错
class VoiceService:
    def speak(self, text):
        # 用打印替代语音播报，不影响核心功能
        print(f"【语音提示】：{text}")