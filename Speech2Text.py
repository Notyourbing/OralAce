import wave

import pyaudio
import io
from openai import OpenAI

client = OpenAI(
    api_key="sk-U3LZPkBCFeLfqcartTW0UDpw9g9BT14myDBtlQN9lzkdGRag",
    base_url="https://api.chatanywhere.tech/v1"
)


def speech_to_text(chatApp):
    # 音频配置
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024

    # 创建 PyAudio 对象
    audio = pyaudio.PyAudio()

    try:
        # 开始录音
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
    except OSError as e:
        print(f"无法打开音频流: {e}")
        return None

    print("正在录音...")
    frames = []

    try:
        # 录音过程
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            if not chatApp.recording_control:
                print("录音结束")
                break
    except OSError as e:
        print(f"录音错误: {e}")
        return None
    finally:
        # 停止录音
        stream.stop_stream()
        stream.close()
        audio.terminate()

    try:
        # 创建内存中的WAV文件
        wav_buffer = io.BytesIO()
        with wave.Wave_write(wav_buffer) as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

            # 将指针移到开始位置
        wav_buffer.seek(0)

        # 直接使用内存中的数据调用 Whisper API
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.wav", wav_buffer),  # 传递文件名和内存中的数据
            language="en"
        )
        return response.text
    except Exception as e:
        print(f"处理音频或调用API时发生错误: {e}")
        return None


