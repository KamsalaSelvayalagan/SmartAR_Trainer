"""
Analytics Screen - Workout Completion Summary with Multiple Pie Charts and Bar Chart
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from backend.models.data_manager import session_analytics

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class AnalyticsScreen(QWidget):
    """Analytics screen showing workout completion summary and charts"""
    
    backRequested = pyqtSignal()
        
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trainee_id = None
        self.rep_totals = {}  # store rep data for pie charts & bar chart
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

        # Top Navigation Bar 
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

        # Page Content Scroll Area
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
        
        # Summary Cards Layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        self.total_sessions_card = self.create_summary_card("Total Sessions", "0")
        cards_layout.addWidget(self.total_sessions_card)

        self.overall_accuracy_card = self.create_summary_card("Rep Based Workouts Overall Accuracy", "0%")
        cards_layout.addWidget(self.overall_accuracy_card)
        
        cards_layout.addStretch()
        
        content_layout.addLayout(cards_layout)
        
        # Rep-Based Workout Table
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

        # Time-Based Workout Table
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
            ["Workout", "Total Time Held (sec)"]
        )
        self.time_table.setMinimumHeight(150)
        time_sec_layout.addWidget(self.time_table)

        content_layout.addWidget(time_section_box)

        # Charts Section (Bar chart + multiple Pie charts side by side)
        charts_section_box = QFrame()
        charts_section_box.setStyleSheet("background: rgba(255, 255, 255, 0.06); border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);")
        charts_layout = QVBoxLayout(charts_section_box)
        charts_layout.setContentsMargins(25, 25, 25, 25)
        charts_layout.setSpacing(60)

        charts_title = QLabel("Performance Visualizations")
        charts_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        charts_title.setStyleSheet("color: #667eea; border: none;")
        charts_layout.addWidget(charts_title)

        # Bar Chart
        self.fig_bar = Figure(dpi=100)
        self.canvas_bar = FigureCanvas(self.fig_bar)
        self.canvas_bar.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.canvas_bar.setMinimumHeight(300)
        self.canvas_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        charts_layout.addWidget(self.canvas_bar)

        # Pie Charts Layout (Side by side)
        self.pie_charts_layout = QHBoxLayout()
        self.pie_charts_layout.setSpacing(20)  # spacing between pie charts
        charts_layout.addLayout(self.pie_charts_layout)

        content_layout.addWidget(charts_section_box)

        # Insight Label
        self.insight_label = QLabel("")
        self.insight_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.insight_label.setStyleSheet("color: #e2e8f0; padding: 10px;")
        content_layout.addWidget(self.insight_label)
        
        scroll.setWidget(content_wrapper)
        main_layout.addWidget(scroll)
        
    def create_summary_card(self, label, value):
        card = QFrame()
        card.setMinimumWidth(220)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
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
        if not self.trainee_id:
            return
            
        session_analytics.load_sessions(self.trainee_id)
        
        # Update summary cards
        self.total_sessions_card.findChild(QLabel, "value").setText(str(session_analytics.total_sessions))
        
        rep_totals = {}
        time_totals = {}

        total_correct_all = 0
        total_wrong_all = 0

        for s in session_analytics.sessions:
            if s.reps_completed > 0:
                if s.exercise_name not in rep_totals:
                    rep_totals[s.exercise_name] = [0, 0, 0]
                rep_totals[s.exercise_name][0] += s.reps_completed
                rep_totals[s.exercise_name][1] += s.correct_reps
                rep_totals[s.exercise_name][2] += s.wrong_reps

                total_correct_all += s.correct_reps
                total_wrong_all += s.wrong_reps

            elif s.duration > 0:
                if s.exercise_name not in time_totals:
                    time_totals[s.exercise_name] = 0
                time_totals[s.exercise_name] += s.duration

        total_all = total_correct_all + total_wrong_all
        overall_acc = 0
        if total_all > 0:
            overall_acc = int((total_correct_all / total_all) * 100)
        self.overall_accuracy_card.findChild(QLabel, "value").setText(f"{overall_acc}%")

        self.rep_totals = rep_totals  # store for charts

        
        # Rep Table
        self.rep_table.setRowCount(len(rep_totals))
        for row, (name, stats) in enumerate(rep_totals.items()):
            total = stats[0]
            correct = stats[1]
            wrong = stats[2]

            self.rep_table.setItem(row, 0, self._create_item(name, Qt.AlignmentFlag.AlignLeft))
            self.rep_table.setItem(row, 1, self._create_item(str(total)))
            self.rep_table.setItem(row, 2, self._create_item(str(correct), color="#48bb78"))
            self.rep_table.setItem(row, 3, self._create_item(str(wrong), color="#f56565"))

        self.rep_table.setSortingEnabled(True)
        self.rep_table.sortItems(1, Qt.SortOrder.DescendingOrder)
        

        # Time Table
        self.time_table.setRowCount(len(time_totals))
        for row, (name, duration) in enumerate(time_totals.items()):
            self.time_table.setItem(row, 0, self._create_item(name, Qt.AlignmentFlag.AlignLeft))
            self.time_table.setItem(row, 1, self._create_item(f"{duration} sec"))


        # Update bar chart
        self.update_bar_chart(rep_totals)

        # Update multiple pie charts side by side
        self.update_multiple_pie_charts(rep_totals)

    def update_bar_chart(self, rep_totals):
        self.fig_bar.clear()
        ax = self.fig_bar.add_subplot(111)

        exercises = []
        accuracies = []

        for name, stats in rep_totals.items():
            total = stats[0]
            correct = stats[1]
            if total > 0:
                acc = (correct / total) * 100
                exercises.append(name)
                accuracies.append(acc)

        ax.bar(exercises, accuracies, color='#667eea',width=0.3)
        ax.set_ylim(0, 100)
        ax.set_ylabel('Accuracy %')
        ax.set_title('Accuracy Percentage per Workout')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        self.fig_bar.tight_layout()
        self.canvas_bar.draw()

    def update_multiple_pie_charts(self, rep_totals):
        # Clear previous pie charts
        while self.pie_charts_layout.count():
            child = self.pie_charts_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        pie_exercises = ["Push-up", "Jumping Jack", "Squat", "Crunches"]

        for ex_name in pie_exercises:
            # 1️⃣ Force identical figure size
            fig = Figure(figsize=(3.5, 3.5), dpi=100)
            fig.patch.set_facecolor('#1e1e2f')

            canvas = FigureCanvas(fig)

            canvas.setMinimumSize(200, 200)
            canvas.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )

            # 3️⃣ Lock axis position (CRITICAL)
            ax = fig.add_axes([0.1, 0.15, 0.8, 0.7])
            ax.set_facecolor('#1e1e2f')

            data = rep_totals.get(ex_name)

            if not data or (data[1] == 0 and data[2] == 0):
                ax.text(
                    0.5, 0.5, 'No Data',
                    ha='center', va='center',
                    fontsize=14, color='white',
                    transform=ax.transAxes
                )
            else:
                correct = data[1]
                wrong = data[2]

                ax.pie(
                    [correct, wrong],
                    colors=['#48bb78', '#f56565'],
                    autopct='%1.1f%%',
                    startangle=90,
                    textprops={'color': 'white', 'fontsize': 10}
                )

            # 4️⃣ Title placement fixed
            ax.set_title(ex_name, color='white', fontsize=14, pad=10)
            ax.axis('equal')

            self.pie_charts_layout.addWidget(canvas)

    def _create_item(self, text, alignment=Qt.AlignmentFlag.AlignCenter, color=None):
        item = QTableWidgetItem(text)
        item.setTextAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
        if color:
            item.setForeground(QColor(color))
        return item
    
    
    def on_profile_clicked(self):
        """Notify main window to show profile"""
        main_win = self.window()
        if hasattr(main_win, "show_profile"):
            main_win.show_profile()
