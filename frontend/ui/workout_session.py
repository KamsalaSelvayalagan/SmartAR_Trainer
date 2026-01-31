"""
Workout Session UI with live camera feedback and guided workflow.
Matches the provided reference design.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QTime, QUrl
from PyQt6.QtGui import QFont
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget


class WorkoutSession(QWidget):
    """Real-time workout session page with camera monitoring"""
    
    sessionEnded = pyqtSignal()
    nextWorkoutRequested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_workout = None
        self.current_index = -1 # Added index tracking
        self.camera_active = False
        
        # Qt 6 Multimedia setup
        self.camera = QCamera()
        self.capture_session = QMediaCaptureSession()
        self.capture_session.setCamera(self.camera)
        
        # Stop watch timer
        self.stopwatch_timer = QTimer()
        self.stopwatch_timer.timeout.connect(self.update_stopwatch)
        self.session_time = QTime(0, 0)
        
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: #0f0c29;") # Dark navy theme
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Navigation Bar (Consistent with Dashboard)
        nav_bar = QFrame()
        nav_bar.setFixedHeight(80)
        nav_bar.setStyleSheet("""
            QFrame {
                background: rgba(15, 12, 41, 0.4);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(50, 0, 50, 0)

        app_title = QLabel("SmartARTrainer")
        app_title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        app_title.setStyleSheet("color: #667eea; background: transparent;")
        nav_layout.addWidget(app_title)
        
        nav_layout.addStretch()

        btn_style = """
            QPushButton {
                background: transparent;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.4);
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(102, 126, 234, 0.3);
            }
        """
        
        self.dash_btn = QPushButton("Dashboard")
        self.dash_btn.setStyleSheet(btn_style.replace("transparent", "rgba(102, 126, 234, 0.8)").replace("1px solid rgba(255, 255, 255, 0.4)", "none"))
        self.dash_btn.clicked.connect(lambda: self.sessionEnded.emit())
        
        self.analytics_btn = QPushButton("Analytics")
        self.analytics_btn.setStyleSheet(btn_style)
        self.analytics_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.analytics_btn.clicked.connect(self.on_analytics_clicked)
        
        self.profile_btn = QPushButton("Profile")
        self.profile_btn.setStyleSheet(btn_style)
        self.profile_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.profile_btn.clicked.connect(self.on_profile_clicked)

        nav_layout.addWidget(self.dash_btn)
        nav_layout.addSpacing(10)
        nav_layout.addWidget(self.analytics_btn)
        nav_layout.addSpacing(10)
        nav_layout.addWidget(self.profile_btn)
        
        main_layout.addWidget(nav_bar)

        # 2. Content Area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(50, 20, 50, 40)
        content_layout.setSpacing(15)

        # Header: Workout Name and Timer
        header_layout = QHBoxLayout()
        
        self.workout_label = QLabel("Workout Name")
        self.workout_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.workout_label.setStyleSheet("color: white; background: transparent;")
        header_layout.addWidget(self.workout_label)
        
        header_layout.addStretch()
        
        self.timer_label = QLabel("00:00")
        self.timer_label.setFont(QFont("Digital-7", 24, QFont.Weight.Bold)) # Digital font if available, fallback to Segoe UI
        self.timer_label.setStyleSheet("color: #667eea; background: transparent;")
        header_layout.addWidget(self.timer_label)
        
        content_layout.addLayout(header_layout)

        # 3. Camera Feed Container
        self.video_widget = QVideoWidget()
        self.video_widget.setFixedHeight(500)
        self.video_widget.setStyleSheet("""
            background: #1a1a1a;
            border-radius: 20px;
            border: 2px solid rgba(255, 255, 255, 0.05);
        """)
        self.capture_session.setVideoOutput(self.video_widget)
        
        content_layout.addWidget(self.video_widget)

        # 4. Controls Footer
        footer_layout = QHBoxLayout()
        
        self.control_btn = QPushButton("Start")
        self.control_btn.setFixedSize(200, 55)
        self.control_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_start_style()
        self.control_btn.clicked.connect(self.toggle_session)
        footer_layout.addWidget(self.control_btn)
        
        footer_layout.addStretch()
        
        self.next_btn = QPushButton("Next Workout")
        self.next_btn.setFixedSize(180, 50)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #764ba2, stop:1 #667eea);
            }
        """)
        self.next_btn.setVisible(False)
        self.next_btn.clicked.connect(self.on_next_clicked)
        footer_layout.addWidget(self.next_btn)
        
        content_layout.addLayout(footer_layout)
        
        main_layout.addWidget(content)

    def on_next_clicked(self):
        """Emit completion signal with current index before moving on"""
        self.nextWorkoutRequested.emit(self.current_index)

    def set_workout(self, workout, index):
        self.current_workout = workout
        self.current_index = index 
        self.workout_label.setText(workout.get("name", "Unknown Workout"))
        self.reset_session()

    def set_placeholder(self):
        # VideoWidget handles its own background
        pass

    def set_start_style(self):
        self.control_btn.setText("Start")
        self.control_btn.setStyleSheet("""
            QPushButton {
                background: #48bb78;
                color: white;
                border-radius: 15px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #38a169;
            }
        """)

    def set_stop_style(self):
        self.control_btn.setText("Stop")
        self.control_btn.setStyleSheet("""
            QPushButton {
                background: #f56565;
                color: white;
                border-radius: 15px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #e53e3e;
            }
        """)

    def toggle_session(self):
        if not self.camera_active:
            self.start_session()
        else:
            self.stop_session()

    def start_session(self):
        self.camera.start()
        self.camera_active = True
        self.stopwatch_timer.start(1000)
        self.set_stop_style()
        self.next_btn.setVisible(False)

    def stop_session(self):
        self.camera.stop()
        self.camera_active = False
        self.stopwatch_timer.stop()
        self.set_placeholder()
        self.set_start_style()
        self.next_btn.setVisible(True)

    def reset_session(self):
        self.stop_session()
        self.next_btn.setVisible(False)
        self.session_time = QTime(0, 0)
        self.timer_label.setText("00:00")

    def update_stopwatch(self):
        self.session_time = self.session_time.addSecs(1)
        self.timer_label.setText(self.session_time.toString("mm:ss"))

    def on_analytics_clicked(self):
        """Notify main window to show analytics"""
        main_win = self.window()
        if hasattr(main_win, "show_analytics"):
            main_win.show_analytics()

    def on_profile_clicked(self):
        """Notify main window to show profile"""
        main_win = self.window()
        if hasattr(main_win, "show_profile"):
            main_win.show_profile()
