from openai import OpenAI
import io
import sounddevice as sd
import soundfile as sf
import threading
import numpy as np

# 初始化客户端
client = OpenAI(
    api_key="sk-U3LZPkBCFeLfqcartTW0UDpw9g9BT14myDBtlQN9lzkdGRag",
    base_url="https://api.chatanywhere.tech/v1"
)

# 定义线程锁，确保音频播放不会重叠
audio_lock = threading.Lock()


def play_audio(audio_data):
    """播放音频"""
    try:
        # 确保只有一个线程能操作音频播放
        with audio_lock:
            # 从内存缓冲区读取音频数据
            with io.BytesIO(audio_data) as audio_buf:
                # 使用 soundfile 读取音频文件
                data, samplerate = sf.read(audio_buf)
                data = data.astype(np.float32)  # 确保音频格式为 float32
                # 播放音频
                sd.play(data, samplerate)
                # 等待音频播放完成
                sd.wait()
    except Exception as e:
        print(f"Error playing audio: {e}")


def text_to_speech(text):
    """将文本转为语音并播放"""
    try:
        # 调用 OpenAI TTS API
        response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text
        )
        if not response.content:
            raise ValueError("Received empty audio data from API.")

            # 在新的守护线程中播放音频
        thread = threading.Thread(target=play_audio, args=(response.content,))
        thread.daemon = True  # 确保线程会在主程序退出时自动终止
        thread.start()
    except Exception as e:
        # 捕获并处理所有异常，防止程序直接崩溃
        print(f"Error in text_to_speech: {e}")


if __name__ == '__main__':
    text_to_speech("Hello, how are you?")
