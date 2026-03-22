import sys
import pygame
import time
import serial
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QLabel, QPushButton, QGridLayout, QTextEdit)
from PySide6.QtCore import (QTimer, Qt, QThread, Signal, Slot)

# ========== 手柄初始化 ==========
pygame.init()
pygame.joystick.init()
pygame.mixer.quit()  # 关闭音频模块，减少资源占用

# ========== 串口子线程（避免阻塞UI） ==========
class SerialThread(QThread):
    log_signal = Signal(str)  # 日志信号（传给UI）
    resp_signal = Signal(str) # 串口回显信号

    def __init__(self, port="COM3", baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.cmd_queue = []  # 指令队列
        self.running = True

    def run(self):
        """子线程主循环：处理串口读写"""
        # 初始化串口
        self.init_serial()

        # 循环处理指令
        while self.running:
            # 处理指令队列
            if self.cmd_queue:
                cmd = self.cmd_queue.pop(0)
                self.send_cmd(cmd)
                time.sleep(0.01)  # 避免指令连发

            # 读取串口回显（非阻塞）
            if self.ser and self.ser.is_open:
                try:
                    resp = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if resp:
                        self.resp_signal.emit(resp)
                except:
                    pass

            time.sleep(0.005)  # 降低CPU占用

    def init_serial(self):
        """串口初始化（子线程中执行）"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.01) # 超时限短至0.01
            time.sleep(0.5)
            self.log_signal.emit(f"串口初始化成功：{self.port} {self.baudrate}")
        except Exception as e:
            self.log_signal.emit(f"串口初始化失败：{e}")
            self.ser = None

    def send_cmd(self, cmd):
        """发送指令（线程安全）"""
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(cmd.encode('utf-8'))
                self.log_signal.emit(f"发送指令：{cmd.strip()}")
            except Exception as e:
                self.log_signal.emit(f"串口发送失败：{e}")
                self.init_serial() # 重试初始化

    def add_cmd(self, cmd):
        """添加指令到队列（UI线程调用）"""
        self.cmd_queue.append(cmd)

    def stop(self):
        """停止线程"""
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.wait()

# ========== 主窗口 ==========
class JoystickControlWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能小车手柄上位机")
        self.setFixedSize(600, 500)

        # 1. 最优先初始化日志缓存（解决log_cache未定义）
        self.log_cache = []

        # 2. 初始化UI（必须完整定义）
        self.init_ui()

        # 3. 初始化计数器和指令缓存
        self.joystick_event_cnt = 0  # 替代static cnt
        self.last_cmd = ""            # 上一次发送的指令

        # 4. 初始化串口子线程
        self.serial_thread = SerialThread(port="COM3", baudrate=9600)
        self.serial_thread.log_signal.connect(self.log)
        self.serial_thread.resp_signal.connect(self.on_serial_resp)
        self.serial_thread.start()

        # 5. 手柄初始化
        self.joystick = None
        self.joystick_available = False
        self.check_joystick()

        # 6. 定时器（降低频率，减少卡顿）
        self.joystick_timer = QTimer()
        self.joystick_timer.setInterval(50)  # 50ms刷新，CPU占用低
        self.joystick_timer.timeout.connect(self.update_joystick_data)
        self.joystick_timer.start()

        # 日志批量更新定时器（减少QTextEdit操作）
        self.log_timer = QTimer()
        self.log_timer.setInterval(200) # 200ms更新一次日志
        self.log_timer.timeout.connect(self.flush_log)
        self.log_timer.start()

    def init_ui(self):
        """完整的UI初始化方法（必须存在）"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignCenter)

        # 状态显示
        self.status_label = QLabel("手柄连接状态：检测中...")
        self.status_label.setStyleSheet("font-size: 16px; margin: 10px; color: #333;")
        self.layout.addWidget(self.status_label)

        # 摇杆数值显示
        self.joystick_grid = QGridLayout()
        self.left_joystick_label = QLabel("左摇杆（前进/后退）：0.0")
        self.left_joystick_label.setStyleSheet("font-size: 14px; margin: 5px;")
        self.joystick_grid.addWidget(self.left_joystick_label, 0, 0)
        self.right_joystick_label = QLabel("右摇杆（左转/右转）：0.0")
        self.right_joystick_label.setStyleSheet("font-size: 14px; margin: 5px;")
        self.joystick_grid.addWidget(self.right_joystick_label, 1, 0)
        self.layout.addLayout(self.joystick_grid)

        # 控制指令显示框
        self.cmd_text = QTextEdit()
        self.cmd_text.setFixedSize(550, 200)
        self.cmd_text.setReadOnly(True)
        self.cmd_text.setStyleSheet("font-size: 12px;")
        self.layout.addWidget(QLabel("控制指令（最新10条）："))
        self.layout.addWidget(self.cmd_text)

        # 退出按钮
        self.exit_btn = QPushButton("退出程序")
        self.exit_btn.setFixedSize(100, 40)
        self.exit_btn.setStyleSheet("font-size: 14px; background: #f44336; color: white; border: none; border-radius: 5px;")
        self.exit_btn.clicked.connect(self.close)
        self.layout.addWidget(self.exit_btn, alignment=Qt.AlignRight)

    def log(self, msg):
        """日志缓存（不直接刷新UI）"""
        self.log_cache.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
        # 缓存最多20条，避免内存占用
        if len(self.log_cache) > 20:
            self.log_cache.pop(0)

    def flush_log(self):
        """批量刷新日志到UI"""
        if self.log_cache:
            # 只保留最新10行
            lines = self.cmd_text.toPlainText().split('\n') + self.log_cache
            if len(lines) > 10:
                lines = lines[-10:]
            self.cmd_text.setText('\n'.join(lines))
            self.log_cache.clear()

    def on_serial_resp(self, resp):
        """处理串口回显"""
        self.log(f"STM32回显：{resp}")

    def check_joystick(self):
        """检测手柄"""
        try:
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.joystick_available = True
                self.status_label.setText(f"手柄连接状态：已连接（{self.joystick.get_name()}）")
                self.log(f"检测到手柄：{self.joystick.get_name()}")
            else:
                self.joystick_available = False
                self.status_label.setText("手柄连接状态：未检测到手柄")
                self.log("未检测到游戏手柄，请连接后重试")
        except Exception as e:
            self.joystick_available = False
            self.status_label.setText("手柄连接状态：检测失败")
            self.log(f"手柄检测失败：{e}")

    def update_joystick_data(self):
        """更新摇杆数据（无语法错误+优化版）"""
        if not self.joystick_available:
            self.check_joystick()
            return

        # 降低pygame事件处理频率（每2次调用一次）
        self.joystick_event_cnt += 1
        if self.joystick_event_cnt % 2 == 0:
            pygame.event.pump()

        # 读取摇杆数据
        left_y = round(-self.joystick.get_axis(1), 2)
        right_x = round(self.joystick.get_axis(2), 2)

        # 死区处理（加大死区，减少误触发）
        dead_zone = 0.2
        left_y = 0.0 if abs(left_y) < dead_zone else left_y
        right_x = 0.0 if abs(right_x) < dead_zone else right_x

        # 更新显示（只在数值变化时更新）
        current_left_text = f"左摇杆（前进/后退）：{left_y}"
        if self.left_joystick_label.text() != current_left_text:
            self.left_joystick_label.setText(current_left_text)
        
        current_right_text = f"右摇杆（左转/右转）：{right_x}"
        if self.right_joystick_label.text() != current_right_text:
            self.right_joystick_label.setText(current_right_text)

        # 生成指令（适配STM32蓝牙#指令;格式）
        cmd = ""
        if left_y > 0.5:
            cmd = "#F;"  # 前进
        elif left_y < -0.5:
            cmd = "#B;"  # 后退
        elif right_x > 0.5:
            cmd = "#R;"  # 右转
        elif right_x < -0.5:
            cmd = "#L;"  # 左转
        else:
            cmd = "#S;"  # 停止/循迹

        # 只发送变化的指令（避免重复发送）
        if self.last_cmd == cmd:
            return
        self.last_cmd = cmd
        self.serial_thread.add_cmd(cmd)

    def closeEvent(self, event):
        """安全退出（清理所有资源）"""
        # 停止定时器
        self.joystick_timer.stop()
        self.log_timer.stop()

        # 发送停止指令
        self.serial_thread.add_cmd("#S;")
        time.sleep(0.1)

        # 停止串口子线程
        self.serial_thread.stop()

        # 清理手柄
        if self.joystick_available:
            self.joystick.quit()
        pygame.quit()

        self.log("程序已安全退出")
        self.flush_log() # 最后刷新一次日志
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # ✅ 完全删除高DPI属性，兼容所有PySide6版本，无报错
    window = JoystickControlWindow()
    window.show()
    sys.exit(app.exec())