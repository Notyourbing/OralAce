import pyaudio
import wave
import keyboard
from openai import OpenAI

client = OpenAI(
    api_key="sk-U3LZPkBCFeLfqcartTW0UDpw9g9BT14myDBtlQN9lzkdGRag",
    base_url="https://api.chatanywhere.tech/v1"
)


def speech_to_text():
    # 音频配置
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    WAVE_OUTPUT_FILENAME = "audio/output.wav"

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

    print("请按下 'S键' 开始说话，并在完成时再次按下 'Q键' 停止录音。")
    keyboard.wait('s')
    print("正在录音...")

    frames = []

    try:
        # 录音过程
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            if keyboard.is_pressed('q'):
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

        # 保存录音
    try:
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
    except OSError as e:
        print(f"保存录音文件错误: {e}")
        return None

        # 调用 OpenAI Whisper API 进行语音识别
    try:
        # print("正在调用 OpenAI Whisper API 进行语音转录...")
        with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",  # 使用 OpenAI 提供的 Whisper 模型
                file=audio_file,
            )
        return response.text
    except Exception as e:
        print(f"调用 OpenAI API 时发生错误: {e}")
        return None


if __name__ == "__main__":
    # 使用示例
    transcribed_text = speech_to_text()
    if transcribed_text:
        print("转换的文本:", transcribed_text)
