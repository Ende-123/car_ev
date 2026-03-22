import sys
import pygame
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QSlider, QSpinBox, QMessageBox,
                               QPushButton, QGroupBox)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

class DualJoystickCarUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # 窗口基础设置
        self.setWindowTitle("智能小车双摇杆控制上位机")
        self.setFixedSize(600, 450)
        self.setStyleSheet("""
            QMainWindow {background-color: #f0f5ff;}
            QGroupBox {font-weight: bold; border: 2px solid #409eff; border-radius: 8px; margin-top: 10px; padding-top: 10px;}
            QLabel {font-size: 14px; color: #303133;}
            QSlider {margin: 10px 0;}
            QSpinBox {font-size: 14px; padding: 5px;}
            QPushButton {background-color: #409eff; color: white; border: none; border-radius: 6px; padding: 8px 16px;}
            QPushButton:hover {background-color: #66b1ff;}
        """)

        # ========== 1. 优先创建并显示界面 ==========
        self.create_ui()
        self.show()

        # ========== 2. 初始化双摇杆手柄 ==========
        self.joystick = None
        self.is_joystick_connected = False
        # 双摇杆参数（左摇杆：横向/纵向；右摇杆：横向/纵向）
        self.left_joystick_x = 0.0  # 左摇杆X轴（-1.0~1.0）
        self.left_joystick_y = 0.0  # 左摇杆Y轴（-1.0~1.0）
        self.right_joystick_x = 0.0 # 右摇杆X轴（-1.0~1.0）
        self.right_joystick_y = 0.0 # 右摇杆Y轴（-1.0~1.0）
        self.init_joystick()

        # ========== 3. 定时器轮询双摇杆输入 ==========
        self.joystick_timer = QTimer(self)
        self.joystick_timer.timeout.connect(self.read_dual_joystick)
        self.joystick_timer.start(30)  # 30ms轮询，更灵敏

        # ========== 4. 初始化控制参数 ==========
        self.steering = 90    # 转向角度（0-180°，左摇杆X控制）
        self.throttle = 0     # 油门（0-100，左摇杆Y控制）
        self.pan = 90         # 云台水平（0-180°，右摇杆X控制）
        self.tilt = 90        # 云台垂直（0-180°，右摇杆Y控制）
        self.update_display()

    def init_joystick(self):
        """初始化手柄，检测双摇杆"""
        try:
            pygame.init()
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.is_joystick_connected = True
                self.joystick_status.setText(f"手柄状态：已连接（{self.joystick.get_name()}）")
                # 显示手柄轴数量（确认双摇杆）
                axis_count = self.joystick.get_numaxes()
                self.axis_info.setText(f"手柄轴数量：{axis_count}（双摇杆需至少4轴）")
            else:
                self.is_joystick_connected = False
                self.joystick_status.setText("手柄状态：未连接")
                QMessageBox.warning(self, "提示", "⚠️ 未检测到游戏手柄！\n请连接带双摇杆的手柄（Xbox/PS/北通）")
        except Exception as e:
            self.is_joystick_connected = False
            self.joystick_status.setText("手柄状态：初始化失败")
            QMessageBox.critical(self, "错误", f"❌ 手柄初始化失败：{str(e)}")

    def create_ui(self):
        """创建双摇杆控制UI界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # 标题
        title_label = QLabel("双摇杆智能小车控制面板")
        title_label.setFont(QFont("微软雅黑", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 手柄状态
        status_layout = QHBoxLayout()
        self.joystick_status = QLabel("手柄状态：初始化中...")
        self.axis_info = QLabel("手柄轴数量：未知")
        status_layout.addWidget(self.joystick_status)
        status_layout.addWidget(self.axis_info)
        main_layout.addLayout(status_layout)

        # ========== 左摇杆控制组（小车运动） ==========
        left_joystick_group = QGroupBox("左摇杆控制（小车运动）")
        left_layout = QVBoxLayout(left_joystick_group)
        
        # 转向角度（左摇杆X）
        steering_layout = QHBoxLayout()
        steering_layout.addWidget(QLabel("转向角度："))
        self.steering_slider = QSlider(Qt.Horizontal)
        self.steering_slider.setRange(0, 180)
        self.steering_slider.setValue(90)
        self.steering_spin = QSpinBox()
        self.steering_spin.setRange(0, 180)
        self.steering_spin.setValue(90)
        self.steering_display = QLabel("当前：90°")
        self.steering_display.setMinimumWidth(80)
        steering_layout.addWidget(self.steering_slider)
        steering_layout.addWidget(self.steering_spin)
        steering_layout.addWidget(self.steering_display)
        left_layout.addLayout(steering_layout)

        # 油门（左摇杆Y）
        throttle_layout = QHBoxLayout()
        throttle_layout.addWidget(QLabel("油门速度："))
        self.throttle_slider = QSlider(Qt.Horizontal)
        self.throttle_slider.setRange(0, 100)
        self.throttle_slider.setValue(0)
        self.throttle_spin = QSpinBox()
        self.throttle_spin.setRange(0, 100)
        self.throttle_spin.setValue(0)
        self.throttle_display = QLabel("当前：0")
        self.throttle_display.setMinimumWidth(80)
        throttle_layout.addWidget(self.throttle_slider)
        throttle_layout.addWidget(self.throttle_spin)
        throttle_layout.addWidget(self.throttle_display)
        left_layout.addLayout(throttle_layout)

        main_layout.addWidget(left_joystick_group)

        # ========== 右摇杆控制组（云台/辅控） ==========
        right_joystick_group = QGroupBox("右摇杆控制（云台/辅控）")
        right_layout = QVBoxLayout(right_joystick_group)
        
        # 云台水平（右摇杆X）
        pan_layout = QHBoxLayout()
        pan_layout.addWidget(QLabel("云台水平："))
        self.pan_slider = QSlider(Qt.Horizontal)
        self.pan_slider.setRange(0, 180)
        self.pan_slider.setValue(90)
        self.pan_spin = QSpinBox()
        self.pan_spin.setRange(0, 180)
        self.pan_spin.setValue(90)
        self.pan_display = QLabel("当前：90°")
        self.pan_display.setMinimumWidth(80)
        pan_layout.addWidget(self.pan_slider)
        pan_layout.addWidget(self.pan_spin)
        pan_layout.addWidget(self.pan_display)
        right_layout.addLayout(pan_layout)

        # 云台垂直（右摇杆Y）
        tilt_layout = QHBoxLayout()
        tilt_layout.addWidget(QLabel("云台垂直："))
        self.tilt_slider = QSlider(Qt.Horizontal)
        self.tilt_slider.setRange(0, 180)
        self.tilt_slider.setValue(90)
        self.tilt_spin = QSpinBox()
        self.tilt_spin.setRange(0, 180)
        self.tilt_spin.setValue(90)
        self.tilt_display = QLabel("当前：90°")
        self.tilt_display.setMinimumWidth(80)
        tilt_layout.addWidget(self.tilt_slider)
        tilt_layout.addWidget(self.tilt_spin)
        tilt_layout.addWidget(self.tilt_display)
        right_layout.addLayout(tilt_layout)

        main_layout.addWidget(right_joystick_group)

        # 功能按钮
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("重新检测手柄")
        self.refresh_btn.clicked.connect(self.init_joystick)
        self.reset_btn = QPushButton("重置所有参数")
        self.reset_btn.clicked.connect(self.reset_all_params)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.reset_btn)
        main_layout.addLayout(btn_layout)

        # 绑定滑块和输入框联动
        self.steering_slider.valueChanged.connect(self.steering_spin.setValue)
        self.steering_spin.valueChanged.connect(self.steering_slider.setValue)
        self.throttle_slider.valueChanged.connect(self.throttle_spin.setValue)
        self.throttle_spin.valueChanged.connect(self.throttle_slider.setValue)
        self.pan_slider.valueChanged.connect(self.pan_spin.setValue)
        self.pan_spin.valueChanged.connect(self.pan_slider.setValue)
        self.tilt_slider.valueChanged.connect(self.tilt_spin.setValue)
        self.tilt_spin.valueChanged.connect(self.tilt_slider.setValue)

        # 绑定手动调节事件
        self.steering_slider.valueChanged.connect(lambda v: self.update_param("steering", v))
        self.throttle_slider.valueChanged.connect(lambda v: self.update_param("throttle", v))
        self.pan_slider.valueChanged.connect(lambda v: self.update_param("pan", v))
        self.tilt_slider.valueChanged.connect(lambda v: self.update_param("tilt", v))

    def read_dual_joystick(self):
        """读取双摇杆输入（适配主流手柄轴映射）"""
        if not self.is_joystick_connected or not self.joystick:
            return
        
        try:
            pygame.event.pump()

            # ========== 双摇杆轴映射（主流手柄通用） ==========
            # 左摇杆：X=0轴，Y=1轴；右摇杆：X=2轴，Y=3轴（Xbox/北通/PS通用）
            self.left_joystick_x = self.joystick.get_axis(0)   # 左摇杆左右（-1左 → +1右）
            self.left_joystick_y = self.joystick.get_axis(1)   # 左摇杆上下（-1上 → +1下）
            self.right_joystick_x = self.joystick.get_axis(2)  # 右摇杆左右（-1左 → +1右）
            self.right_joystick_y = self.joystick.get_axis(3)  # 右摇杆上下（-1上 → +1下）

            # ========== 左摇杆 → 小车运动 ==========
            # 转向角度：左摇杆X（-1~1 → 0~180°）
            new_steering = int((self.left_joystick_x + 1) * 90)
            new_steering = max(0, min(180, new_steering))
            # 油门速度：左摇杆Y（-1~1 → 0~100，上推为加速）
            new_throttle = int((-self.left_joystick_y + 1) * 50)
            new_throttle = max(0, min(100, new_throttle))

            # ========== 右摇杆 → 云台控制 ==========
            # 云台水平：右摇杆X（-1~1 → 0~180°）
            new_pan = int((self.right_joystick_x + 1) * 90)
            new_pan = max(0, min(180, new_pan))
            # 云台垂直：右摇杆Y（-1~1 → 0~180°）
            new_tilt = int((-self.right_joystick_y + 1) * 90)
            new_tilt = max(0, min(180, new_tilt))

            # 更新控件值（仅当变化超过阈值时更新，避免抖动）
            if abs(new_steering - self.steering) > 0:
                self.steering = new_steering
                self.steering_slider.setValue(self.steering)
            if abs(new_throttle - self.throttle) > 0:
                self.throttle = new_throttle
                self.throttle_slider.setValue(self.throttle)
            if abs(new_pan - self.pan) > 0:
                self.pan = new_pan
                self.pan_slider.setValue(self.pan)
            if abs(new_tilt - self.tilt) > 0:
                self.tilt = new_tilt
                self.tilt_slider.setValue(self.tilt)

            # 实时显示摇杆原始值（调试用）
            self.axis_info.setText(
                f"左摇杆(X:{self.left_joystick_x:.2f}, Y:{self.left_joystick_y:.2f}) | "
                f"右摇杆(X:{self.right_joystick_x:.2f}, Y:{self.right_joystick_y:.2f})"
            )

        except Exception as e:
            self.is_joystick_connected = False
            self.joystick_status.setText("手柄状态：读取失败")
            print(f"双摇杆读取错误：{e}")

    def update_param(self, param_name, value):
        """更新单个参数并显示"""
        setattr(self, param_name, value)
        self.update_display()
        # 打印参数（用于串口/网络发送）
        print(f"{param_name} = {value}")

    def update_display(self):
        """更新所有参数显示"""
        self.steering_display.setText(f"当前：{self.steering}°")
        self.throttle_display.setText(f"当前：{self.throttle}")
        self.pan_display.setText(f"当前：{self.pan}°")
        self.tilt_display.setText(f"当前：{self.tilt}°")

    def reset_all_params(self):
        """重置所有参数为默认值"""
        self.steering = 90
        self.throttle = 0
        self.pan = 90
        self.tilt = 90
        self.steering_slider.setValue(90)
        self.throttle_slider.setValue(0)
        self.pan_slider.setValue(90)
        self.tilt_slider.setValue(90)
        self.update_display()
        QMessageBox.information(self, "提示", "所有参数已重置为默认值！")

    def closeEvent(self, event):
        """关闭窗口释放资源"""
        reply = QMessageBox.question(self, "确认关闭", "是否关闭双摇杆控制上位机？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.is_joystick_connected and self.joystick:
                self.joystick.quit()
            pygame.quit()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    QApplication.setStyle("Fusion")
    app = QApplication(sys.argv)
    window = DualJoystickCarUI()
    sys.exit(app.exec())