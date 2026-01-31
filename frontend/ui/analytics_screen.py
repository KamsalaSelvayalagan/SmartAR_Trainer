"""
Analytics Screen - Workout Completion Summary
Professional UI with tables and summary cards matching the overall theme
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from backend.models.data_manager import session_analytics

class AnalyticsScreen(QWidget):
    """Analytics screen showing workout completion summary"""
    
    backRequested = pyqtSignal()
        
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trainee_id = None
        self.init_ui()
        
    def set_user(self, user_data):
        """Set user and refresh analytics data"""
        self.trainee_id = user_data.get("trainee_id")
        self.refresh_data()

    def init_ui(self):
        """Initialize the UI"""
        self.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Navigation Bar (Consistent)
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
                background: %s;
                color: white;
                border: %s;
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
        self.dash_btn.setStyleSheet(btn_style % ("transparent", "1px solid rgba(255, 255, 255, 0.4)"))
        self.dash_btn.clicked.connect(self.backRequested.emit)
        
        self.analytics_btn = QPushButton("Analytics")
        self.analytics_btn.setStyleSheet(btn_style % ("rgba(102, 126, 234, 0.8)", "none"))
        
        self.profile_btn = QPushButton("Profile")
        self.profile_btn.setStyleSheet(btn_style % ("transparent", "1px solid rgba(255, 255, 255, 0.4)"))
        self.profile_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.profile_btn.clicked.connect(self.on_profile_clicked)

        nav_layout.addWidget(self.dash_btn)
        nav_layout.addSpacing(10)
        nav_layout.addWidget(self.analytics_btn)
        nav_layout.addSpacing(10)
        nav_layout.addWidget(self.profile_btn)
        
        main_layout.addWidget(nav_bar)

        # 2. Page Content with Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content_wrapper = QWidget()
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(50, 30, 50, 40)
        content_layout.setSpacing(25)
        
        # Title
        title = QLabel("Workout Completion Summary")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        content_layout.addWidget(title)
        
        # Summary Overview
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        self.total_sessions_card = self.create_summary_card("Total Sessions", "0")
        cards_layout.addWidget(self.total_sessions_card)
        cards_layout.addStretch()
        
        content_layout.addLayout(cards_layout)
        
        # Rep-Based Workout Table Section
        rep_section_box = QFrame()
        rep_section_box.setStyleSheet("background: rgba(255, 255, 255, 0.04); border-radius: 20px; border: 1px solid rgba(255,255,255,0.08);")
        rep_sec_layout = QVBoxLayout(rep_section_box)
        rep_sec_layout.setContentsMargins(25, 25, 25, 25)

        rep_section = QLabel("Rep-Based Workouts")
        rep_section.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        rep_section.setStyleSheet("color: #667eea; border: none;")
        rep_sec_layout.addWidget(rep_section)
        rep_sec_layout.addSpacing(15)
        
        self.rep_table = self.create_workout_table(
            ["Workout", "Total Reps", "Correct Reps", "Wrong Reps"]
        )
        self.rep_table.setMinimumHeight(250)
        rep_sec_layout.addWidget(self.rep_table)
        
        content_layout.addWidget(rep_section_box)

        # Time-Based Workout Table Section
        time_section_box = QFrame()
        time_section_box.setStyleSheet("background: rgba(255, 255, 255, 0.04); border-radius: 20px; border: 1px solid rgba(255,255,255,0.08);")
        time_sec_layout = QVBoxLayout(time_section_box)
        time_sec_layout.setContentsMargins(25, 25, 25, 25)

        time_section = QLabel("Time-Based Workouts")
        time_section.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        time_section.setStyleSheet("color: #667eea; border: none;")
        time_sec_layout.addWidget(time_section)
        time_sec_layout.addSpacing(15)
        
        self.time_table = self.create_workout_table(
            ["Workout", "Total Time Held"]
        )
        self.time_table.setMinimumHeight(150)
        time_sec_layout.addWidget(self.time_table)

        content_layout.addWidget(time_section_box)
        
        scroll.setWidget(content_wrapper)
        main_layout.addWidget(scroll)
        
    def create_summary_card(self, label, value):
        """Create a professional summary card widget"""
        card = QFrame()
        card.setFixedWidth(250)
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 rgba(102, 126, 234, 0.15),
                                           stop:1 rgba(118, 75, 162, 0.15));
                border: 2px solid rgba(102, 126, 234, 0.3);
                border-radius: 20px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        val_widget = QLabel(value)
        val_widget.setObjectName("value")
        val_widget.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        val_widget.setStyleSheet("color: white; border: none;")
        val_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(val_widget)

        lbl_widget = QLabel(label.upper())
        lbl_widget.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl_widget.setStyleSheet("color: #667eea; letter-spacing: 1px; border: none;")
        lbl_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_widget)
        
        return card
        
    def create_workout_table(self, headers):
        """Create a highly styled workout statistics table"""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                border: none;
                gridline-color: rgba(255, 255, 255, 0.05);
                color: #e2e8f0;
                font-size: 14px;
                outline: none;
            }
            QTableWidget::item {
                padding: 15px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QHeaderView::section {
                background: rgba(102, 126, 234, 0.1);
                color: #667eea;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
                text-transform: uppercase;
                border-bottom: 2px solid rgba(102, 126, 234, 0.4);
            }
        """)
        
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, len(headers)):
            table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
            
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        
        return table
        
    def refresh_data(self):
        """Refresh analytics data from DB"""
        if not self.trainee_id:
            return
            
        session_analytics.load_sessions(self.trainee_id)
        
        # Update Summary Card
        self.total_sessions_card.findChild(QLabel, "value").setText(str(session_analytics.total_sessions))
        
        # Aggregate Workouts
        rep_totals = {} # workout_name -> [total, correct, wrong]
        time_totals = {} # workout_name -> duration

        for s in session_analytics.sessions:
            if s.reps_completed > 0:
                if s.exercise_name not in rep_totals:
                    rep_totals[s.exercise_name] = [0, 0, 0]
                rep_totals[s.exercise_name][0] += s.reps_completed
                rep_totals[s.exercise_name][1] += s.correct_reps
                rep_totals[s.exercise_name][2] += s.wrong_reps
            elif s.duration > 0:
                if s.exercise_name not in time_totals:
                    time_totals[s.exercise_name] = 0
                time_totals[s.exercise_name] += s.duration

        # Populate Rep Table
        self.rep_table.setRowCount(len(rep_totals))
        for row, (name, stats) in enumerate(rep_totals.items()):
            # Name
            self.rep_table.setItem(row, 0, self._create_item(name, Qt.AlignmentFlag.AlignLeft))
            # Total Reps
            self.rep_table.setItem(row, 1, self._create_item(str(stats[0])))
            # Correct
            self.rep_table.setItem(row, 2, self._create_item(str(stats[1]), color="#48bb78"))
            # Wrong
            self.rep_table.setItem(row, 3, self._create_item(str(stats[2]), color="#f56565"))

        # Populate Time Table
        self.time_table.setRowCount(len(time_totals))
        for row, (name, duration) in enumerate(time_totals.items()):
            self.time_table.setItem(row, 0, self._create_item(name, Qt.AlignmentFlag.AlignLeft))
            self.time_table.setItem(row, 1, self._create_item(f"{duration} sec"))

    def on_profile_clicked(self):
        """Notify main window to show profile"""
        main_win = self.window()
        if hasattr(main_win, "show_profile"):
            main_win.show_profile()

    def _create_item(self, text, alignment=Qt.AlignmentFlag.AlignCenter, color=None):
        item = QTableWidgetItem(text)
        item.setTextAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
        if color:
            item.setForeground(QColor(color))
        return item
