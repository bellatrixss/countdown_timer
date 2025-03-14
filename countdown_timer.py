import sys
import time
import platform
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTimeEdit, QSlider, QSizeGrip)
from PyQt5.QtCore import Qt, QTimer, QTime, QPoint
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QCursor

class CountdownTimer(QWidget):
    def __init__(self):
        super().__init__()
        
        # 设置窗口无边框和透明背景
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 初始化UI
        self.initUI()
        
        # 初始化变量
        self.is_counting = False
        self.remaining_seconds = 0
        self.original_seconds = 0
        self.drag_position = None
        self.is_folded = False  # 添加折叠状态变量
        
        # 设置定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        
    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 创建一个带有圆角和背景色的容器
        self.container = QWidget(self)
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            #container {
                background-color: rgba(40, 44, 52, 0.9);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setSpacing(5)  # 减小组件之间的间距
        
        # 顶部控制栏
        top_bar = QWidget()
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        top_bar.setFixedHeight(20)  # 固定顶部栏高度
        # 根据操作系统调整按钮顺序和样式
        if platform.system() == "Darwin":  # macOS
            # 关闭按钮
            self.close_btn = QPushButton("×")
            self.close_btn.setFixedSize(20, 20)
            self.close_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 80, 80, 0.8);
                    color: white;
                    border-radius: 10px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(255, 80, 80, 1.0);
                }
            """)
            self.close_btn.clicked.connect(self.close)
            
            # 最小化按钮
            self.minimize_btn = QPushButton("−")
            self.minimize_btn.setFixedSize(20, 20)
            self.minimize_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 190, 0, 0.8);
                    color: white;
                    border-radius: 10px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(255, 190, 0, 1.0);
                }
            """)
            self.minimize_btn.clicked.connect(self.showMinimized)
            
            # 折叠按钮
            self.fold_btn = QPushButton("▲")
            self.fold_btn.setFixedSize(20, 20)
            self.fold_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 180, 140, 0.8);
                    color: white;
                    border-radius: 10px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(0, 180, 140, 1.0);
                }
            """)
            self.fold_btn.clicked.connect(self.toggle_fold)
            
            # Mac风格：按钮从左到右排列
            top_bar_layout.addWidget(self.close_btn)
            top_bar_layout.addWidget(self.minimize_btn)
            top_bar_layout.addWidget(self.fold_btn)
        else:
            # 关闭按钮
            self.close_btn = QPushButton("×")
            self.close_btn.setFixedSize(20, 20)
            self.close_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 80, 80, 0.8);
                    color: white;
                    border-radius: 10px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(255, 80, 80, 1.0);
                }
            """)
            self.close_btn.clicked.connect(self.close)
            
            # 最小化按钮
            self.minimize_btn = QPushButton("−")
            self.minimize_btn.setFixedSize(20, 20)
            self.minimize_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 190, 0, 0.8);
                    color: white;
                    border-radius: 10px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(255, 190, 0, 1.0);
                }
            """)
            self.minimize_btn.clicked.connect(self.showMinimized)

            # 折叠按钮
            self.fold_btn = QPushButton("▲")
            self.fold_btn.setFixedSize(20, 20)
            self.fold_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 180, 140, 0.8);
                    color: white;
                    border-radius: 10px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(0, 180, 140, 1.0);
                }
            """)
            self.fold_btn.clicked.connect(self.toggle_fold)
            top_bar_layout.addWidget(self.close_btn)
            top_bar_layout.addWidget(self.minimize_btn)
            top_bar_layout.addWidget(self.fold_btn)
        
        # 透明度标签和滑块容器
        self.opacity_container = QWidget()
        opacity_layout = QHBoxLayout(self.opacity_container)
        opacity_layout.setContentsMargins(0, 0, 0, 0)
        
        # 透明度滑块
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(90)
        self.opacity_slider.setFixedWidth(80)
        self.opacity_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 10px;
                height: 10px;
                margin: -3px 0;
                border-radius: 5px;
            }
            QSlider::sub-page:horizontal {
                background: rgba(0, 120, 215, 0.8);
                border-radius: 2px;
            }
        """)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        
        # 添加透明度标签和滑块到容器
        opacity_layout.addWidget(QLabel("透明度"))
        opacity_layout.addWidget(self.opacity_slider)
        
        # 添加到顶部栏布局
        
        top_bar_layout.addStretch(1)
        top_bar_layout.addWidget(self.opacity_container)
        
        # 倒计时显示标签
        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Arial", 36, QFont.Bold))
        self.time_label.setStyleSheet("color: white;")
        self.time_label.setMinimumHeight(50)  # 设置最小高度确保显示完整
        
        # 创建控制面板容器（用于折叠功能）
        self.control_panel = QWidget()
        control_layout = QVBoxLayout(self.control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)
        
        # 时间选择器
        time_selector_layout = QHBoxLayout()
        
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.time_edit.setTime(QTime(0, 10, 0))  # 默认10分钟
        self.time_edit.setStyleSheet("""
            QTimeEdit {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border-radius: 5px;
                padding: 5px;
                selection-background-color: rgba(0, 120, 215, 0.8);
            }
        """)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 开始/暂停按钮
        self.start_pause_btn = QPushButton("开始")
        self.start_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 120, 215, 0.8);
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 120, 215, 1.0);
            }
        """)
        self.start_pause_btn.clicked.connect(self.toggle_countdown)
        
        # 重置按钮
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 100, 100, 0.8);
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(100, 100, 100, 1.0);
            }
        """)
        self.reset_btn.clicked.connect(self.reset_countdown)
        
        # 添加按钮到布局
        button_layout.addWidget(self.start_pause_btn)
        button_layout.addWidget(self.reset_btn)
        
        # 添加时间选择器到布局
        time_selector_layout.addWidget(QLabel("设置时间:"))
        time_selector_layout.addWidget(self.time_edit)
        
        # 将时间选择器和按钮添加到控制面板
        control_layout.addLayout(time_selector_layout)
        control_layout.addLayout(button_layout)

        # 添加大小调整手柄
        size_grip = QSizeGrip(self)
        size_grip.setStyleSheet("background: rgba(255, 255, 255, 0.2);")

        # 创建一个底部布局来放置大小调整手柄
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(size_grip)
        
        # 添加所有组件到容器布局
        container_layout.addWidget(top_bar)
        container_layout.addWidget(self.time_label)
        container_layout.addWidget(self.control_panel)
        container_layout.addLayout(bottom_layout)
        
        # 将容器添加到主布局
        main_layout.addWidget(self.container)
        self.setLayout(main_layout)
        
        # 设置初始窗口大小和位置
        self.resize(300, 200)
        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle('桌面倒计时')
        
        # 应用样式
        self.setStyleSheet("""
            QLabel {
                color: white;
            }
            QWidget {
                font-family: 'Microsoft YaHei', Arial;
            }
        """)
        
        # 设置初始透明度
        self.change_opacity(self.opacity_slider.value())

    def toggle_fold(self):
        self.is_folded = not self.is_folded
        
        if self.is_folded:
            # 折叠状态
            self.fold_btn.setText("▼")
            self.control_panel.hide()
            self.opacity_container.hide()  # 隐藏透明度控制
            
            # 调整折叠后的高度和布局
            self.setFixedHeight(110)  # 减小整体高度
            # 减小时间标签的上边距，使其更靠近顶部按钮
            self.time_label.setContentsMargins(0, 0, 0, 20)
            # 调整字体显示区域
            self.time_label.setMinimumHeight(70)
            
            # 调整容器布局的边距，减小顶部和底部边距
            self.container.layout().setContentsMargins(10, 5, 10, 5)
        else:
            # 展开状态
            self.fold_btn.setText("▲")
            self.control_panel.show()
            self.opacity_container.show()  # 显示透明度控制
            self.setMinimumHeight(200)  # 恢复最小高度
            self.setMaximumHeight(16777215)  # 恢复最大高度 (QWIDGETSIZE_MAX)
            # 恢复正常边距
            self.time_label.setContentsMargins(0, 0, 0, 0)
            # 恢复正常高度
            self.time_label.setMinimumHeight(50)
            # 恢复容器布局的正常边距
            self.container.layout().setContentsMargins(10, 10, 10, 10)
        
        # 更新窗口大小
        self.adjustSize()
        
    def toggle_countdown(self):
        if not self.is_counting:
            # 获取时间编辑器的时间
            time = self.time_edit.time()
            self.remaining_seconds = time.hour() * 3600 + time.minute() * 60 + time.second()
            
            if self.remaining_seconds <= 0:
                return
            
            self.original_seconds = self.remaining_seconds
            self.is_counting = True
            self.start_pause_btn.setText("暂停")
            self.time_edit.setEnabled(False)
            self.timer.start(1000)  # 每秒更新一次
        else:
            self.is_counting = False
            self.start_pause_btn.setText("继续")
            self.timer.stop()
    
    def update_countdown(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_display()
            
            # 根据剩余时间的百分比更改颜色
            progress = self.remaining_seconds / self.original_seconds if self.original_seconds > 0 else 0
            if progress > 0.5:
                color = "rgba(0, 200, 0, 1.0)"  # 绿色
            elif progress > 0.2:
                color = "rgba(255, 165, 0, 1.0)"  # 橙色
            else:
                color = "rgba(255, 50, 50, 1.0)"  # 红色
                
            # 保持字体大小不变，只改变颜色
            self.time_label.setStyleSheet(f"color: {color}; font-size: 36pt; font-weight: bold;")
        else:
            self.timer.stop()
            self.is_counting = False
            self.start_pause_btn.setText("开始")
            self.time_edit.setEnabled(True)
            self.time_label.setStyleSheet("color: white; font-size: 36pt; font-weight: bold;")
    
    def update_display(self):
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60
        self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def reset_countdown(self):
        self.timer.stop()
        self.is_counting = False
        self.start_pause_btn.setText("开始")
        self.time_edit.setEnabled(True)
        self.time_label.setText("00:00:00")
        self.time_label.setStyleSheet("color: white; font-size: 36pt; font-weight: bold;")
    
    def change_opacity(self, value):
        opacity = value / 100.0
        self.setWindowOpacity(opacity)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.drag_position = None
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CountdownTimer()
    window.show()
    sys.exit(app.exec_())