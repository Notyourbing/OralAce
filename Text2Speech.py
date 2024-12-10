from openai import OpenAI
import io
from pydub import AudioSegment
from pydub.playback import play

client = OpenAI(
    api_key="sk-U3LZPkBCFeLfqcartTW0UDpw9g9BT14myDBtlQN9lzkdGRag",
    base_url="https://api.chatanywhere.tech/v1"
)


def text_to_speech(text):
    try:
        # print("正在调用 OpenAI TTS API 生成语音...")

        # 调用 OpenAI TTS API
        response = client.audio.speech.create(
            model="tts-1",  # 使用 OpenAI 提供的 TTS 模型
            voice="shimmer",  # 选择语音风格，可根据需要调整
            input=text  # 输入的文本内容
        )

        # 将生成的音频加载到 BytesIO 对象中
        audio_data = io.BytesIO(response.content)

        # 使用 pydub 播放音频
        # print("正在播放生成的语音...")
        audio_segment = AudioSegment.from_file(audio_data, format="mp3")

        play(audio_segment)

        # print("播放完成！")
    except Exception as e:
        print(f"调用 OpenAI TTS API 时发生错误: {e}")


if __name__ == '__main__':
    text_to_speech("Hello, how are you?")
