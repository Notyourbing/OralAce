import sys
import openai
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon, QPalette, QBrush, QPixmap, QPainter, QColor
from PyQt5.QtCore import QSize
from Text2Speech import text_to_speech
from Speech2Text import speech_to_text
import threading
from qfluentwidgets import ComboBox
import random

openai.api_key = "sk-proj-UJomPMNYs592LOa7HhU0T3BlbkFJG4LSECNT5VsFCKJFc1jp"
scene_set = ["Daily life", "Shopping", "Education", "Social life", "Traveling abroad"]
scene_dl = ["ordeing in a cantee", "tidying the house", "hailing a taxi", "asking for the way"]
scene_sh = ["shopping at a sports shop", "buying some fruits", "asking for after-sales service"]
scene_ed = ["talking about tommorrow's math test", "asking information for your offers"]
scene_sl = ["making a new friend", "planning a trip with friends"]
scene_ta = ["booking a hotel", "checking in at the airport"]

class ChatApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.messages = []

    def initUI(self):
        self.setWindowTitle("Oral English Practice Program")
        self.setGeometry(100, 100, 1500, 1000)

        # 设置背景
        palette = QPalette()
        pixmap = QPixmap('bg.jpg').scaled(2700, 1600)
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
        icon = QtGui.QIcon("icon.png")
        self.setWindowIcon(icon)

        # 设置背景色和默认字体颜色
        #self.setStyleSheet("background-color: #f7f9fc; color: #2c3e50;")
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

        self.instruction_label = QtWidgets.QLabel(
            "Instructions: Please choose a scene set to get a random scene in that set. When you get ready, press the 'Start Practice' button at the bottom of the page. After your AI partner begin the conversation, you can talk with her after pressing 'S' on your keyboard. When you finish talking, you can press 'Q' on your keyboard to end and wait for your partner's response. If you want to end this conversation, just speak the single word 'close'.")
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
        self.picture_button.setIcon(QIcon(QPixmap('q_m.jpg')))
        self.picture_button.setIconSize(QSize(450, 275))
        self.picture_button.setFixedSize(450, 275)
        self.scene_vlayout.addWidget(self.picture_button, alignment=QtCore.Qt.AlignCenter)

        # 将垂直布局添加到网格布局中
        self.layout.addLayout(self.scene_vlayout, 1, 0, 1, 1)

        # Start Practice按钮
        self.start_button = QtWidgets.QPushButton("Start Practice")
        self.start_button.setFont(QtGui.QFont("Georgia", 16, QtGui.QFont.Bold))
        self.start_button.setIcon(QIcon(QPixmap('play.png')))
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
        # self.layout.addWidget(self.start_button, 3, 0, alignment=QtCore.Qt.AlignCenter)

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

    def message_to_str(self):
        # 将消息列表转换为字符串
        messages_str = ""
        for message in self.messages:
            messages_str += f"Role: {message['role']}, Content: {message['content']}\n"
        return messages_str

    def create_reply(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
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
        self.start_button.setEnabled(False)
        c_scene_set = self.scene_combobox.currentText()
        if (c_scene_set == "Daily life"):
            self.picture_button.setIcon(QIcon(QPixmap('dl.jpg')))
            self.picture_button.setIconSize(QSize(450, 275))
            scene=random.choice(scene_dl)
        elif (c_scene_set == "Shopping"):
            self.picture_button.setIcon(QIcon(QPixmap('sh.jpg')))
            self.picture_button.setIconSize(QSize(450, 275))
            scene=random.choice(scene_sh)
        elif (c_scene_set == "Education"):
            self.picture_button.setIcon(QIcon(QPixmap('ed.jpg')))
            self.picture_button.setIconSize(QSize(450, 275))
            scene=random.choice(scene_ed)
        elif (c_scene_set == 'Social life'):
            self.picture_button.setIcon(QIcon(QPixmap('sl.jpg')))
            self.picture_button.setIconSize(QSize(450, 275))
            scene=random.choice(scene_sl)
        elif (c_scene_set == 'Traveling abroad'):
            self.picture_button.setIcon(QIcon(QPixmap('ta.jpg')))
            self.picture_button.setIconSize(QSize(450, 275))
            scene=random.choice(scene_ta)

        self.chat_display.append(f"Scene:{scene}")

        prompt = (f"I want you to act as an English speaking practice partner. "
                  f"I will speak to you in English and you will reply to me in English to practice my spoken English. "
                  f"I want you to keep your reply neat, limiting the reply to 100 words. "
                  f"Please pretend we are talking in the scenario: {scene}. "
                  f"Now let's start practicing, you could ask me a question first. "
                  f"Just start the practicing without expressing your happiness to help me"
                  f"Please input your question without saying 'sure': ")
        self.messages = [
            {"role": "system", "content": prompt},
        ]
        # self.update_chat_display("System", prompt)
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            max_tokens=100,
        )
        response = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": response})
        self.update_chat_display("Partner", response)
        text_to_speech(response)

        while True:
            user_input = speech_to_text()
            if user_input:
                # self.input_field.append(f"You:{user_input}")
                self.chat_display.append(f"You:{user_input}")
            if user_input == "close":
                break
            reply = self.create_reply(user_input)
            self.update_chat_display("Partner", reply)
            text_to_speech(reply)

        messages_str = self.message_to_str()
        part1 = "I want you to act as a spoken English teacher and improver. \
                   Here is an English conversation involving two people, an assistant and a user."
        part2 = ("Please assess the user's oral English expression in this dialogue, and I am the user.\
                    considering aspects such as grammar, vocabulary, fluency, authenticity, and more.\
                    And don't forget to correct my grammar mistakes, typos, and factual errors.\
                    Additionally, provide some suggestions for improving my oral English expression.\
                    Please limit your reply to 150 words or less.")

        request = part1 + messages_str + part2

        evaluation = openai.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=request,
            max_tokens=500,
            n=1,
            stop=None,
            temperature=1,
        )
        self.update_chat_display("Evaluation", evaluation.choices[0].text)
        text_to_speech(evaluation.choices[0].text)
        self.start_button.setEnabled(True)

    def update_chat_display(self, role, content):
        self.chat_display.append(f"{role}: {content}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    chat_app = ChatApp()
    chat_app.show()
    sys.exit(app.exec_())