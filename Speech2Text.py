import pyaudio
import wave
import speech_recognition as sr
import keyboard

def speech_to_text():
    # 音频配置
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    WAVE_OUTPUT_FILENAME = "output.wav"

    # 创建PyAudio对象
    audio = pyaudio.PyAudio()

    try:
        # 开始录音
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    except OSError as e:
        print(f"无法打开音频流: {e}")
        return None

    # print("请按下 'S键' 开始说话，并在完成时再次按下 'Q键' 停止录音。")
    # keyboard.wait('s')
    # print("正在录音...")

    frames = []

    print("正在录音")
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

    # 使用 SpeechRecognition 进行语音识别
    r = sr.Recognizer()
    try:
        with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
            audio = r.record(source)
        # 转换语音为文本
        text = r.recognize_google(audio, language='en-US')
        return text
    except sr.UnknownValueError:
        print("无法识别语音")
        return ""
    except sr.RequestError as e:
        print(f"无法连接到Google API，错误原因：{e}")
        return None
if __name__ == "__main__":
    # 使用示例
    transcribed_text = speech_to_text()
    if transcribed_text:
        print("转换的文本:", transcribed_text)
