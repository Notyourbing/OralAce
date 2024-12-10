from openai import OpenAI
import io
import sounddevice as sd
import soundfile as sf
import threading

client = OpenAI(
    api_key="sk-U3LZPkBCFeLfqcartTW0UDpw9g9BT14myDBtlQN9lzkdGRag",
    base_url="https://api.chatanywhere.tech/v1"
)


def play_audio(audio_data):
    try:
        # 从内存缓冲区读取音频数据
        with io.BytesIO(audio_data) as audio_buf:
            # 读取音频文件
            data, samplerate = sf.read(audio_buf)
            # 播放音频
            sd.play(data, samplerate)
            # 等待音频播放完成
            sd.wait()
    except Exception as e:
        print(f"Error playing audio: {e}")


def text_to_speech(text):
    try:
        # 调用 OpenAI TTS API
        response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text
        )

        # 在新线程中播放音频
        thread = threading.Thread(target=play_audio, args=(response.content,))
        thread.daemon = True
        thread.start()

    except Exception as e:
        print(f"Error in text_to_speech: {e}")


if __name__ == '__main__':
    text_to_speech("Hello, how are you?")
