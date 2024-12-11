import os
import random
import sys
import threading

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPalette, QBrush, QPixmap, QPainter, QColor
from PyQt5.QtWidgets import QPushButton
from openai import OpenAI
from qfluentwidgets import ComboBox

from Speech2Text import speech_to_text
from Text2Speech import text_to_speech

client = OpenAI(
    api_key="sk-Jqjsjxuap8LEKcROc7iTbiZ2B93Vs9bNdrAMw8u3dyxltimg",
    base_url="https://api.chatanywhere.tech/v1"
)

scene_set = ["Daily life", "Shopping", "Education", "Social life", "Traveling abroad"]
scene_daily_life = ["ordeing in a cantee", "tidying the house", "hailing a taxi", "asking for the way"]
scene_shopping = ["shopping at a sports shop", "buying some fruits", "asking for after-sales service"]
scene_education = ["talking about tommorrow's math test", "asking information for your offers"]
scene_social_life = ["making a new friend", "planning a trip with friends"]
scene_traveling_abroad = ["booking a hotel", "checking in at the airport"]


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ChatApp(QtWidgets.QWidget):
    recording_control = False

    def __init__(self):
        super().__init__()
        self.running = None
        self.quit_button = None
        self.chat_display = None
        self.exit_button = None
        self.record_button = None
        self.start_button = None
        self.picture_button = None
        self.scene_combobox = None
        self.instruction_label = None
        self.scene_vlayout = None
        self.title_label = None
        self.layout = None
        self.initUI()
        self.messages = []

    def initUI(self):
        self.setWindowTitle("Oral English Practice Program")
        self.setGeometry(100, 100, 1500, 1000)

        # 设置背景
        palette = QPalette()
        pixmap = QPixmap(resource_path('image/background.jpg')).scaled(2700, 1600)
        transparent_pixmap = QPixmap(pixmap.size())
        transparent_pixmap.fill(QColor(255, 255, 255, 255))
        painter = QPainter(transparent_pixmap)
        painter.setOpacity(0.5)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        brush = QBrush(transparent_pixmap)
        palette.setBrush(QPalette.Window, brush)
        self.setPalette(palette)

        # 设置icon
        icon = QtGui.QIcon(resource_path("image/icon.png"))
        self.setWindowIcon(icon)

        # 设置背景色和默认字体颜色
        # layout.addWidget(widget, row, column, row_span, column_span, alignment) 函数参数
        self.setStyleSheet("color: #2c3e50;")

        # 设置全局字体大小
        default_font = QtGui.QFont("Cambria", 13)
        QtWidgets.QApplication.setFont(default_font)

        # layout是网格式布局
        self.layout = QtWidgets.QGridLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(40)

        # 创建标题标签
        self.title_label = QtWidgets.QLabel("Scenario Dialogue")
        title_font = QtGui.QFont("Georgia", 24, QtGui.QFont.Bold)
        self.title_label.setFont(title_font)

        # 设置字体颜色为蓝色
        self.title_label.setStyleSheet("color: #2980b9;")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)  # 设置居中对齐
        self.layout.addWidget(self.title_label, 0, 0, 1, 2)

        # 创建垂直布局来包含instruction_label、scene_combobox
        self.scene_vlayout = QtWidgets.QVBoxLayout()
        self.scene_vlayout.setSpacing(10)

        # 指导说明标签
        instruction_text = (
            "Instructions:\n"
            "1. Select a conversation scenario from the dropdown menu\n"
            "2. Click 'Start Practice' to begin\n"
            "3. Use the green button to start/stop recording your response\n"
            "4. Click 'End Conversation' to finish and get your evaluation"
        )
        self.instruction_label = QtWidgets.QLabel(instruction_text)
        self.instruction_label.setWordWrap(True)
        instruction_font = QtGui.QFont("Comic Sans MS", 11)
        self.instruction_label.setFont(instruction_font)
        self.instruction_label.setStyleSheet("border: 2px dashed #2980b9; border-radius: 10px; padding: 10px;")

        # 圆角下拉菜单
        self.scene_combobox = ComboBox(self)
        self.scene_combobox.addItems(scene_set)
        self.scene_combobox.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.scene_combobox.setMinimumSize(500, 40)
        self.scene_combobox.setFont(QtGui.QFont("Arial", 12))

        # 将instruction_label和scene_combobox添加到垂直布局
        self.scene_vlayout.addWidget(self.instruction_label, alignment=QtCore.Qt.AlignCenter)
        self.scene_vlayout.addWidget(self.scene_combobox, alignment=QtCore.Qt.AlignCenter)

        # 添加图片
        self.picture_button = QPushButton(self)
        self.picture_button.setIcon(QIcon(QPixmap(resource_path('image/q_m.jpg'))))
        self.picture_button.setIconSize(QSize(450, 275))
        self.picture_button.setFixedSize(450, 275)
        self.scene_vlayout.addWidget(self.picture_button, alignment=QtCore.Qt.AlignCenter)

        # 将垂直布局添加到网格布局中
        self.layout.addLayout(self.scene_vlayout, 1, 0, 1, 1)

        # Start Practice按钮
        self.start_button = QtWidgets.QPushButton("Start Practice")
        self.start_button.setFont(QtGui.QFont("Georgia", 16, QtGui.QFont.Bold))
        self.start_button.setIcon(QIcon(QPixmap(resource_path('image/play.png'))))
        self.start_button.setIconSize(QSize(30, 30))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: #FFFFFF;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6f99;
            }
        """)
        self.start_button.setFixedSize(280, 60)
        self.start_button.clicked.connect(self.start_practice)
        self.scene_vlayout.addWidget(self.start_button, alignment=QtCore.Qt.AlignCenter)

        # Record button
        self.record_button = QtWidgets.QPushButton("Start Recording")
        self.record_button.setCheckable(True)  # Make it a toggle button
        self.record_button.setFont(QtGui.QFont("Georgia", 16, QtGui.QFont.Bold))
        # self.record_button.setIcon(QIcon(QPixmap('image/record.png')))  # Optional: set a record icon
        self.record_button.setIconSize(QSize(30, 30))
        self.record_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: #FFFFFF;
                        border-radius: 20px;
                    }
                    QPushButton:checked {
                        background-color: #e67e22;
                    }
                    QPushButton:hover {
                        background-color: #27ae60;
                    }
                    QPushButton:pressed {
                        background-color: #1e8449;
                    }
                """)
        self.record_button.setFixedSize(280, 60)
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setEnabled(False)  # Initially disabled
        self.scene_vlayout.addWidget(self.record_button, alignment=QtCore.Qt.AlignCenter)

        # 退出对话按钮
        self.exit_button = self.exit_button = QtWidgets.QPushButton("End Conversation")
        self.exit_button.setFont(QtGui.QFont("Georgia", 16, QtGui.QFont.Bold))
        self.exit_button.setIcon(QIcon(QPixmap(resource_path('image/exit.png'))))
        self.exit_button.setIconSize(QSize(30, 30))
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #FFFFFF;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #992d22;
            }
        """)
        self.exit_button.setFixedSize(280, 60)
        self.exit_button.setEnabled(False)  # 默认禁用
        self.exit_button.clicked.connect(self.end_conversation)

        # 将exit_button添加到布局中
        self.scene_vlayout.addWidget(self.exit_button, alignment=QtCore.Qt.AlignCenter)

        # 聊天显示框
        self.chat_display = QtWidgets.QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                border: 2px dashed #2980b9;
                border-radius: 10px;
                padding: 10px;
                background: rgba(255, 255, 255, 0%);
            }
        """)
        self.layout.addWidget(self.chat_display, 1, 1, 1, 1)

        # 设置列的宽度策略
        self.layout.setColumnStretch(0, 1)  # 第一列占的宽度比例
        self.layout.setColumnStretch(1, 3)  # 第二列占的宽度比例
        self.layout.setColumnMinimumWidth(0, 300)  # 第一列最小宽度

        self.setLayout(self.layout)

        # 在initUI()中添加图片按钮
        self.quit_button = QtWidgets.QPushButton("")
        self.quit_button.setStyleSheet("""
            QPushButton {
                border: none;  /* 移除边框 */
                background: transparent; /* 背景透明 */
                border-radius: 20px;  /* 半径为宽度和高度的一半，形成圆形 */
            }
            QPushButton:hover {
                background: rgba(255, 0, 0, 0.2); /* 鼠标悬停时加轻微红色背景 */
            }
            QPushButton:pressed {
                background: rgba(255, 0, 0, 0.5); /* 按下时加深红色背景 */
            }
        """)
        self.quit_button.setFixedSize(40, 40)  # 按钮大小与图片大小一致
        self.quit_button.setIcon(QIcon(resource_path("image/close_button.png")))  # 设置图片为按钮图标
        self.quit_button.setIconSize(QSize(40, 40))  # 图标大小等于按钮大小
        self.quit_button.clicked.connect(self.close)  # 点击按钮退出程序

        # 添加到布局（左上角）
        self.layout.addWidget(self.quit_button, 0, 0, 1, 1, QtCore.Qt.AlignLeft)

        # 添加到布局（左上角）
        self.layout.addWidget(self.quit_button, 0, 0, 1, 1, QtCore.Qt.AlignLeft)

    def message_to_str(self):
        # 将消息列表转换为字符串
        messages_str = ""
        for message in self.messages:
            messages_str += f"Role: {message['role']}, Content: {message['content']}\n"
        return messages_str

    def create_reply(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            max_tokens=100,
        )
        self.messages.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content

    def start_practice(self):
        self.chat_display.clear()
        thread = threading.Thread(target=self.run_practice)
        thread.start()

    def run_practice(self):
        global scene, user_input
        self.start_button.setEnabled(False)
        self.exit_button.setEnabled(True)
        c_scene_set = self.scene_combobox.currentText()
        if c_scene_set == "Daily life":
            self.picture_button.setIcon(QIcon(QPixmap(resource_path('image/dl.jpg'))))
            self.picture_button.setIconSize(QSize(450, 275))
            scene = random.choice(scene_daily_life)
        elif c_scene_set == "Shopping":
            self.picture_button.setIcon(QIcon(QPixmap(resource_path('image/sh.jpg'))))
            self.picture_button.setIconSize(QSize(450, 275))
            scene = random.choice(scene_shopping)
        elif c_scene_set == "Education":
            self.picture_button.setIcon(QIcon(QPixmap(resource_path('image/ed.jpg'))))
            self.picture_button.setIconSize(QSize(450, 275))
            scene = random.choice(scene_education)
        elif c_scene_set == 'Social life':
            self.picture_button.setIcon(QIcon(QPixmap(resource_path('image/sl.jpg'))))
            self.picture_button.setIconSize(QSize(450, 275))
            scene = random.choice(scene_social_life)
        elif c_scene_set == 'Traveling abroad':
            self.picture_button.setIcon(QIcon(QPixmap(resource_path('image/ta.jpg'))))
            self.picture_button.setIconSize(QSize(450, 275))
            scene = random.choice(scene_traveling_abroad)

        self.chat_display.append(f"Scene:{scene}")

        prompt = (f"I want you to act as an English speaking practice partner. "
                  f"I will speak to you in English and you will reply to me in English to practice my spoken English. "
                  f"I want you to keep your reply neat, limiting the reply to 100 words. "
                  f"Please pretend we are talking in the scenario: {scene}. "
                  f"Now let's start practicing, you could ask me a question first. "
                  f"Just start the practicing without expressing your happiness to help me"
                  f"Please input your question without saying 'sure': ")
        self.messages = [
            {"role": "system", "content": prompt}
        ]
        # self.update_chat_display("System", prompt)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            max_tokens=100,
        )
        response = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": response})
        text_to_speech(response)
        self.update_chat_display("Partner", response)
        self.record_button.setEnabled(True)
        self.running = True  # 控制对话循环
        while self.running:
            print("请按下绿色按钮")
            while self.running:
                if self.recording_control:
                    user_input = speech_to_text(self)
                    break
            if not self.running:  # 检查是否已终止对话
                break
            if user_input:
                self.chat_display.append(f"You:{user_input}")

            reply = self.create_reply(user_input)
            text_to_speech(reply)
            self.update_chat_display("Partner", reply)

        messages_str = self.message_to_str()
        part1 = ("I want you to act as a spoken English teacher and improver. "
                 "Here is an English conversation involving two people, an assistant and a user.")
        part2 = ("Please assess the user's oral English expression in this dialogue, and I am the user."
                 "considering aspects such as grammar, vocabulary, fluency, authenticity, and more."
                 "And don't forget to correct my grammar mistakes, typos, and factual errors."
                 "Additionally, provide some suggestions for improving my oral English expression."
                 "Please limit your reply to 150 words or less."
                 "Keep your answers out of bold font")
        request = part1 + messages_str + part2
        final_message = [{"role": "user", "content": request}]

        evaluation = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=final_message,
            max_tokens=500,
        )
        text_to_speech(evaluation.choices[0].message.content)
        self.update_chat_display("Evaluation", evaluation.choices[0].message.content)
        self.start_button.setEnabled(True)
        self.exit_button.setEnabled(False)  # 禁用exit_button

    def update_chat_display(self, role, content):
        self.chat_display.append(f"{role}: {content}")

    def end_conversation(self):
        self.running = False  # Set the conversation loop flag to False
        self.recording_control = False  # Reset recording flag
        self.record_button.setChecked(False)
        self.record_button.setText("Evaluating...")
        self.record_button.setEnabled(False)
        self.exit_button.setEnabled(False)
        self.start_button.setEnabled(True)

    def toggle_recording(self):
        if self.record_button.isChecked():
            # Start Recording
            self.record_button.setText("Stop Recording")
            self.recording_control = True
            # Optionally, provide visual feedback
        else:
            # Stop Recording
            self.record_button.setText("Start Recording")
            self.recording_control = False


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    chat_app = ChatApp()
    chat_app.show()
    sys.exit(app.exec_())
