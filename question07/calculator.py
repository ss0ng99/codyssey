import sys
from PyQt5.QtWidgets import (
  QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt


class Calculator:
  def __init__(self):
    self.reset()

  def reset(self):
    self.current = ''
    self.operator = ''
    self.result = None

  def input_number(self, num):
    if num == '.' and '.' in self.current:
      return
    self.current += num

  def add(self):
    self._compute_pending()
    self.operator = '+'

  def subtract(self):
    self._compute_pending()
    self.operator = '-'

  def multiply(self):
    self._compute_pending()
    self.operator = '*'

  def divide(self):
    self._compute_pending()
    self.operator = '/'

  def negative_positive(self):
    if self.current.startswith('-'):
      self.current = self.current[1:]
    elif self.current:
      self.current = '-' + self.current

  def percent(self):
    if self.current:
      try:
        self.current = str(float(self.current) / 100)
      except:
        self.current = 'Error'

  def equal(self):
    self._compute_pending(final=True)
    result = self.format_result(self.result)
    self.current = result
    self.result = None
    self.operator = ''
    return result

  def _compute_pending(self, final=False):
    try:
      if self.current:
        if self.result is None:
          self.result = float(self.current)
        else:
          b = float(self.current)
          if self.operator == '+':
            self.result += b
          elif self.operator == '-':
            self.result -= b
          elif self.operator == '*':
            self.result *= b
          elif self.operator == '/':
            self.result = self.result / b if b != 0 else float('inf')
      self.current = ''
    except Exception:
      self.result = None
      self.current = 'Error'

  def format_result(self, value):
    try:
      value = float(value)
      rounded = round(value, 6)
      text = str(rounded)
      if '.' in text:
        text = text.rstrip('0').rstrip('.') if text.rstrip('0').rstrip('.') else '0'
      return text
    except:
      return 'Error'


class CalculatorUI(QWidget):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("iPhone Style Calculator")
    self.setFixedSize(360, 540)
    self.calc = Calculator()
    self.init_ui()

  def init_ui(self):
    layout = QVBoxLayout()

    # Display
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

        # 버튼 클래스 속성 설정
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

    # 클래스별 공통 스타일 적용
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

    if text in '0123456789.':
      self.calc.input_number(text)
      self.update_display(self.calc.current)
    elif text == '+':
      self.calc.add()
      self.update_display(self.calc.format_result(self.calc.result))
    elif text == '-':
      self.calc.subtract()
      self.update_display(self.calc.format_result(self.calc.result))
    elif text == '*':
      self.calc.multiply()
      self.update_display(self.calc.format_result(self.calc.result))
    elif text == '/':
      self.calc.divide()
      self.update_display(self.calc.format_result(self.calc.result))
    elif text == 'AC':
      self.calc.reset()
      self.update_display('')
    elif text == '+/-':
      self.calc.negative_positive()
      self.update_display(self.calc.current)
    elif text == '%':
      self.calc.percent()
      self.update_display(self.calc.current)
    elif text == '=':
      result = self.calc.equal()
      self.update_display(result)

  def update_display(self, text):
    if len(text) <= 10:
      font_size = 40
    elif len(text) <= 15:
      font_size = 30
    elif len(text) <= 20:
      font_size = 24
    else:
      font_size = 18

    self.display.setStyleSheet(f"""
      background-color: black;
      color: white;
      font-size: {font_size}px;
      padding: 10px;
      border: none;
    """)
    self.display.setText(text)


if __name__ == "__main__":
  app = QApplication(sys.argv)
  calc_ui = CalculatorUI()
  calc_ui.show()
  sys.exit(app.exec_())
