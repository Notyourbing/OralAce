import pyaudio
import io
import wave
import traceback
from openai import OpenAI

client = OpenAI(
    api_key="sk-U3LZPkBCFeLfqcartTW0UDpw9g9BT14myDBtlQN9lzkdGRag",
    base_url="https://api.chatanywhere.tech/v1"
)


def speech_to_text(chatApp):
    try:
        # 音频配置
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024

        # 创建 PyAudio 对象
        audio = pyaudio.PyAudio()
        stream = None
        frames = []

        try:
            # 开始录音
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
            print("正在录音...")

            # 录音过程
            while True:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                    if not chatApp.recording_control:
                        print("录音结束")
                        break
                except Exception as e:
                    print(f"录音过程中出错: {e}")
                    return None

        except Exception as e:
            print(f"设置录音设备时出错: {e}")
            return None

        finally:
            # 确保资源正确关闭
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    print(f"关闭音频流时出错: {e}")
            try:
                audio.terminate()
            except Exception as e:
                print(f"终止PyAudio时出错: {e}")

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

            print("正在转换语音...")

            # 直接使用内存中的数据调用 Whisper API
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=("audio.wav", wav_buffer),
                language="en"
            )

            print("转换完成")
            return response.text

        except Exception as e:
            print(f"API调用或音频处理错误: {e}")
            print("详细错误信息:")
            traceback.print_exc()
            return None

    except Exception as e:
        print(f"发生未预期的错误: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # 使用示例
    transcribed_text = speech_to_text()
    if transcribed_text:
        print("转换的文本:", transcribed_text)
