import demo
from PySide6.QtWidgets import QApplication, QDialog  # 把 QMainWindow 改成 QDialog

class MainWindow(QDialog, demo.Ui_Dialog):  # 继承 QDialog + Ui_Dialog
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 加载 UI 界面

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.setWindowTitle("Smart Car Control")  # 设置窗口标题
    window.show()  # 显示窗口
    app.exec()  # 启动事件循环python py/host_computer.py