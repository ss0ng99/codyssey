import sys
from PyQt5.QtWidgets import (
  QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt


class Calculator(QWidget):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("iPhone Style Calculator")
    self.setFixedSize(360, 540)
    self.init_ui()
    self.expression = ""

  def init_ui(self):
    layout = QVBoxLayout()

    # 디스플레이
    self.display = QLineEdit()
    self.display.setReadOnly(True)
    self.display.setAlignment(Qt.AlignRight)
    self.display.setFixedHeight(100)
    self.display.setStyleSheet("""
      background-color: black;
      color: white;
      font-size: 40px;
      padding: 10px;
      border: none;
    """)
    layout.addWidget(self.display)

    # 버튼 텍스트
    buttons = [
      ['AC', '+/-', '%', '/'],
      ['7', '8', '9', '*'],
      ['4', '5', '6', '-'],
      ['1', '2', '3', '+'],
      ['0', '.', '=']
    ]

    grid = QGridLayout()

    for row, row_buttons in enumerate(buttons):
      col_offset = 0
      for col, btn_text in enumerate(row_buttons):
        button = QPushButton(btn_text)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setMinimumSize(80, 80)

        # 클래스 할당
        if btn_text in ['AC', '+/-', '%']:
          button.setProperty("class", "function")
        elif btn_text in ['/', '*', '-', '+', '=']:
          button.setProperty("class", "operator")
        else:
          button.setProperty("class", "number")

        if btn_text == '0':
          grid.addWidget(button, row, col, 1, 2)
          col_offset = 1
        else:
          grid.addWidget(button, row, col + col_offset)

        button.clicked.connect(self.on_button_clicked)

    layout.addLayout(grid)
    self.setLayout(layout)

    # 공통 스타일 한 번에 적용
    self.setStyleSheet("""
      QWidget {
        background-color: black;
      }

      QPushButton[class="number"] {
        background-color: #505050;
        color: white;
        font-size: 24px;
        border-radius: 40px;
      }
      QPushButton[class="number"]:pressed {
        background-color: #303030;
      }

      QPushButton[class="operator"] {
        background-color: #f39c12;
        color: white;
        font-size: 24px;
        border-radius: 40px;
      }
      QPushButton[class="operator"]:pressed {
        background-color: #e67e22;
      }

      QPushButton[class="function"] {
        background-color: #a5a5a5;
        color: black;
        font-size: 24px;
        border-radius: 40px;
      }
      QPushButton[class="function"]:pressed {
        background-color: #909090;
      }
    """)

  def on_button_clicked(self):
    sender = self.sender()
    text = sender.text()

    if text == 'AC':
      self.expression = ''
    elif text == '+/-':
      if self.expression.startswith('-'):
        self.expression = self.expression[1:]
      elif self.expression:
        self.expression = '-' + self.expression
    elif text == '%':
      try:
        self.expression = str(float(self.expression) / 100)
      except:
        self.expression = "Error"
    elif text == '=':
      try:
        self.expression = str(eval(self.expression))
      except:
        self.expression = "Error"
    else:
      self.expression += text

    self.display.setText(self.format_display(self.expression))

  def format_display(self, value):
    try:
      if '.' in value:
        return value
      return f"{int(value):,}"
    except:
      return value


if __name__ == "__main__":
  app = QApplication(sys.argv)
  calc = Calculator()
  calc.show()
  sys.exit(app.exec_())
